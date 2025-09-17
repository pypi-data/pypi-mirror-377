import importlib
import importlib.util
import shutil
import sys
import tempfile
import threading
import zipfile
from pathlib import Path
from typing import Any


def _load_from_directory(dir_path: Path, module_name: str) -> Any:
    """从目录加载模块"""
    original_path = sys.path.copy()
    try:
        if str(dir_path) not in sys.path:
            sys.path.insert(0, str(dir_path))

        return importlib.import_module(module_name)
    finally:
        sys.path[:] = original_path


def _load_direct_from_zip(archive_path: Path, module_name: str) -> Any:
    """直接从 zip 加载（不解压）"""
    original_path = sys.path.copy()
    try:
        if str(archive_path) not in sys.path:
            sys.path.insert(0, str(archive_path))

        return importlib.import_module(module_name)
    finally:
        sys.path[:] = original_path


class DynamicLoader:
    """动态模块/对象加载器 - 支持多种格式的包"""

    def __init__(self):
        self._loaded_modules: dict[str, Any] = {}
        self._temp_dirs: list[str] = []
        self._original_path = sys.path.copy()
        self._lock = threading.Lock()

    def load_from_file(self, file_path: str, module_name: str | None = None) -> Any:
        """从 .py 文件加载模块"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        module_name = module_name or file_path.stem

        with self._lock:
            if module_name in self._loaded_modules:
                return self._loaded_modules[module_name]

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                raise ImportError(f"无法创建模块规范: {file_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._loaded_modules[module_name] = module
            return module

    def load_from_package(self, package_path: str, module_name: str) -> Any:
        """从包目录或 whl/zip 文件加载模块"""
        package_path = Path(package_path)

        with self._lock:
            cache_key = f"{package_path}::{module_name}"
            if cache_key in self._loaded_modules:
                return self._loaded_modules[cache_key]

            # 处理不同类型的包
            if package_path.is_dir():
                module = _load_from_directory(package_path, module_name)
            elif package_path.suffix in [".whl", ".zip"]:
                module = self._load_from_archive(package_path, module_name)
            else:
                raise ValueError(f"不支持的包格式: {package_path}")

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
            except:
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

    def get_object(self, package_path: str, module_name: str, object_name: str) -> Any:
        """获取指定对象（类、函数等）"""
        module = self.load_from_package(package_path, module_name)

        if not hasattr(module, object_name):
            raise AttributeError(f"模块 '{module_name}' 没有属性 '{object_name}'")

        return getattr(module, object_name)

    def get_class(
        self, package_path: str, module_name: str, class_name: str, *args, **kwargs
    ) -> Any:
        """获取类并实例化"""
        cls = self.get_object(package_path, module_name, class_name)

        if not isinstance(cls, type):
            raise TypeError(f"'{class_name}' 不是一个类")

        return cls(*args, **kwargs)

    def get_function(self, package_path: str, module_name: str, func_name: str) -> Any:
        """获取函数"""
        func = self.get_object(package_path, module_name, func_name)

        if not callable(func):
            raise TypeError(f"'{func_name}' 不是可调用对象")

        return func

    def call_function(
        self, package_path: str, module_name: str, func_name: str, *args, **kwargs
    ) -> Any:
        """调用函数并返回结果"""
        func = self.get_function(package_path, module_name, func_name)
        return func(*args, **kwargs)

    def list_objects(
        self, package_path: str, module_name: str, filter_type: type | None = None
    ) -> list[str]:
        """列出模块中的对象"""
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

    def cleanup(self):
        """清理临时文件和缓存"""
        with self._lock:
            # 清理临时目录
            for temp_dir in self._temp_dirs:
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            self._temp_dirs.clear()

            # 清理缓存
            self._loaded_modules.clear()

            # 恢复原始路径
            sys.path[:] = self._original_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
