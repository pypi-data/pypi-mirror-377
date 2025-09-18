import importlib
import shutil
import sys
import tempfile
import threading
import zipfile
from pathlib import Path
from typing import Any


def _load_direct_from_zip(archive_path: Path, module_name: str) -> Any:
    """直接从 zip 加载（不解压）"""
    original_path = sys.path.copy()
    try:
        if str(archive_path) not in sys.path:
            sys.path.insert(0, str(archive_path))

        return importlib.import_module(module_name)
    finally:
        sys.path[:] = original_path


class ArchiveLoader:
    """动态模块/对象加载器 - 支持 whl/zip 文件加载"""

    def __init__(self):
        self._loaded_modules: dict[str, Any] = {}
        self._temp_dirs: list[str] = []
        self._original_path = sys.path.copy()
        self._lock = threading.Lock()
        self._registered_packages: set[str] = set()  # 记录已注册的包

    def load_from_package(self, package_path: str, module_name: str) -> Any:
        """从 whl/zip 文件加载模块"""
        package_path = Path(package_path)

        with self._lock:
            cache_key = f"{package_path}::{module_name}"
            if cache_key in self._loaded_modules:
                return self._loaded_modules[cache_key]

            # 只处理 whl/zip 文件
            if package_path.suffix in [".whl", ".zip"]:
                module = self._load_from_archive(package_path, module_name)
            else:
                raise ValueError(
                    f"不支持的包格式: {package_path}，只支持 .whl 和 .zip 文件"
                )

            self._loaded_modules[cache_key] = module
            return module

    def _load_with_extraction(self, archive_path: Path, module_name: str) -> Any:
        """解压后加载"""
        temp_dir = tempfile.mkdtemp(prefix="dynamic_loader_")
        self._temp_dirs.append(temp_dir)

        try:
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            original_path = sys.path.copy()
            try:
                sys.path.insert(0, temp_dir)
                return importlib.import_module(module_name)
            finally:
                sys.path[:] = original_path

        except Exception as e:
            # 清理失败的临时目录
            try:
                shutil.rmtree(temp_dir)
                self._temp_dirs.remove(temp_dir)
            except (OSError, ValueError):
                pass
            raise e

    def _load_from_archive(
        self, archive_path: Path, module_name: str, extract: bool = True
    ) -> Any:
        """从 zip/whl 文件加载模块"""
        if extract:
            return self._load_with_extraction(archive_path, module_name)
        else:
            return _load_direct_from_zip(archive_path, module_name)

    def register_package_modules(self, package_path: str) -> None:
        """将包中的所有模块注册到Python模块系统，解决依赖问题"""
        package_key = str(Path(package_path))

        if package_key in self._registered_packages:
            return  # 已经注册过了

        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"包文件不存在: {package_path}")

        with self._lock:
            # 解压到临时目录
            temp_dir = tempfile.mkdtemp(prefix="package_modules_")
            self._temp_dirs.append(temp_dir)

            try:
                with zipfile.ZipFile(package_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # 将解压目录添加到sys.path
                if temp_dir not in sys.path:
                    sys.path.insert(0, temp_dir)

                # 自动发现并预加载模块
                self._discover_modules(temp_dir)

                self._registered_packages.add(package_key)
                print(f"包模块已注册: {package_path}")

            except Exception as e:
                # 清理失败的临时目录
                try:
                    shutil.rmtree(temp_dir)
                    self._temp_dirs.remove(temp_dir)
                except (OSError, ValueError):
                    pass
                raise e

    def _discover_modules(self, base_dir: str) -> None:
        """发现并预加载目录中的Python模块"""
        base_path = Path(base_dir)
        modules_found = []

        # 收集所有Python模块
        for py_file in base_path.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue

            rel_path = py_file.relative_to(base_path)

            if py_file.name == "__init__.py":
                # 包目录
                if len(rel_path.parts) > 1:
                    module_name = ".".join(rel_path.parts[:-1])
                    modules_found.append(module_name)
            else:
                # 普通模块
                module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
                module_name = ".".join(module_parts)
                modules_found.append(module_name)

        # 按层次排序，先加载父包
        modules_found.sort(key=lambda x: (x.count("."), x))

        # 预加载模块（静默失败）
        for module_name in modules_found:
            try:
                if module_name not in sys.modules:
                    importlib.import_module(module_name)
            except (OSError, ValueError):
                pass

    def _inject_to_caller_module(self, class_name: str, cls: type) -> None:
        """将类注入到调用者模块"""
        import inspect

        frame = inspect.currentframe()
        try:
            # 向上查找调用者
            caller_frame = frame.f_back.f_back  # 跳过当前方法调用
            if caller_frame is None:
                return

            caller_globals = caller_frame.f_globals
            caller_module_name = caller_globals.get("__name__")

            if not caller_module_name:
                return

            # 注入到调用者模块
            if caller_module_name in sys.modules:
                setattr(sys.modules[caller_module_name], class_name, cls)

            # 处理 __main__ 和 main 模块的互相注入
            if caller_module_name == "__main__" and "main" in sys.modules:
                setattr(sys.modules["main"], class_name, cls)
            elif caller_module_name == "main" and "__main__" in sys.modules:
                setattr(sys.modules["__main__"], class_name, cls)

        except Exception:
            pass  # 静默忽略注入失败
        finally:
            del frame

    def get_object(
        self,
        package_path: str,
        module_name: str,
        object_name: str,
        register_dependencies: bool = False,
    ) -> Any:
        """获取指定对象（类、函数等）

        Args:
            package_path: 包路径
            module_name: 模块名
            object_name: 对象名
            register_dependencies: 是否注册包中的所有模块（解决依赖问题）
        """
        # 如果需要注册依赖
        if register_dependencies:
            self.register_package_modules(package_path)

        module = self.load_from_package(package_path, module_name)

        if not hasattr(module, object_name):
            raise AttributeError(f"模块 '{module_name}' 没有属性 '{object_name}'")

        return getattr(module, object_name)

    def get_class(
        self,
        package_path: str,
        module_name: str,
        class_name: str,
        register_dependencies: bool = False,
        auto_inject: bool = False,
        *args,
        **kwargs,
    ) -> Any:
        """获取类并实例化

        Args:
            package_path: 包路径
            module_name: 模块名
            class_name: 类名
            register_dependencies: 是否注册包中的所有模块（解决依赖问题）
            auto_inject: 是否自动将类注入到调用者模块
            *args, **kwargs: 实例化参数
        """
        cls = self.get_object(
            package_path, module_name, class_name, register_dependencies
        )

        if not isinstance(cls, type):
            raise TypeError(f"'{class_name}' 不是一个类")

        # 自动注入到调用者模块
        if auto_inject:
            self._inject_to_caller_module(class_name, cls)

        return cls(*args, **kwargs)

    def get_class_definition(
        self,
        package_path: str,
        module_name: str,
        class_name: str,
        register_dependencies: bool = False,
        auto_inject: bool = False,
    ) -> type:
        """获取类定义（不实例化）

        Args:
            package_path: 包路径
            module_name: 模块名
            class_name: 类名
            register_dependencies: 是否注册包中的所有模块（解决依赖问题）
            auto_inject: 是否自动将类注入到调用者模块
        """
        cls = self.get_object(
            package_path, module_name, class_name, register_dependencies
        )

        if not isinstance(cls, type):
            raise TypeError(f"'{class_name}' 不是一个类")

        # 自动注入到调用者模块
        if auto_inject:
            self._inject_to_caller_module(class_name, cls)

        return cls

    def inject_class_to_module(
        self,
        package_path: str,
        source_module: str,
        class_name: str,
        target_module_name: str,
        register_dependencies: bool = False,
    ) -> type:
        """将类注入到指定模块中，使其可以被直接导入

        Args:
            package_path: 包路径
            source_module: 源模块名
            class_name: 类名
            target_module_name: 目标模块名
            register_dependencies: 是否注册包中的所有模块（解决依赖问题）
        """
        cls = self.get_class_definition(
            package_path, source_module, class_name, register_dependencies
        )

        # 获取目标模块
        target_module = sys.modules.get(target_module_name)
        if target_module is None:
            target_module = importlib.import_module(target_module_name)

        # 将类注入到目标模块
        setattr(target_module, class_name, cls)

        return cls

    def get_class_with_full_support(
        self, package_path: str, module_name: str, class_name: str, *args, **kwargs
    ) -> Any:
        """获取类并实例化，自动处理所有依赖和注入

        这是一个便捷方法，等同于:
        get_class(..., register_dependencies=True, auto_inject=True)
        """
        return self.get_class(
            package_path,
            module_name,
            class_name,
            register_dependencies=True,
            auto_inject=True,
            *args,
            **kwargs,
        )

    def get_function(
        self,
        package_path: str,
        module_name: str,
        func_name: str,
        register_dependencies: bool = False,
    ) -> Any:
        """获取函数

        Args:
            package_path: 包路径
            module_name: 模块名
            func_name: 函数名
            register_dependencies: 是否注册包中的所有模块（解决依赖问题）
        """
        func = self.get_object(
            package_path, module_name, func_name, register_dependencies
        )

        if not callable(func):
            raise TypeError(f"'{func_name}' 不是可调用对象")

        return func

    def list_objects(
        self,
        package_path: str,
        module_name: str,
        filter_type: type | None = None,
        register_dependencies: bool = False,
    ) -> list[str]:
        """列出模块中的对象

        Args:
            package_path: 包路径
            module_name: 模块名
            filter_type: 过滤类型
            register_dependencies: 是否注册包中的所有模块（解决依赖问题）
        """
        # 如果需要注册依赖
        if register_dependencies:
            self.register_package_modules(package_path)

        module = self.load_from_package(package_path, module_name)

        objects = []
        for name in dir(module):
            if name.startswith("_"):
                continue

            obj = getattr(module, name)
            if filter_type is None or isinstance(obj, filter_type):
                objects.append(name)

        return objects

    def reload_module(self, package_path: str, module_name: str) -> Any:
        """重新加载模块"""
        with self._lock:
            cache_key = f"{package_path}::{module_name}"
            if cache_key in self._loaded_modules:
                del self._loaded_modules[cache_key]

            return self.load_from_package(package_path, module_name)

    def get_temp_dirs(self) -> list[str]:
        """获取当前的临时目录列表"""
        return self._temp_dirs.copy()

    def cleanup(self):
        """清理临时文件和缓存"""
        with self._lock:
            # 清理临时目录
            for temp_dir in self._temp_dirs:
                try:
                    shutil.rmtree(temp_dir)
                except (OSError, ValueError):
                    pass
            self._temp_dirs.clear()

            # 清理缓存
            self._loaded_modules.clear()
            self._registered_packages.clear()

            # 恢复原始路径
            sys.path[:] = self._original_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


__all__ = ["ArchiveLoader"]
