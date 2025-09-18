import ast
import importlib.util
import json
import zipfile
from pathlib import Path

from rain_ai.core.serialize.schemas import ZipExampleConfig


def _is_stdlib(module_name: str) -> bool:
    """检查是否为标准库模块"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False

        if spec.origin is None:  # 内置模块
            return True

        # 检查是否在标准库路径中
        stdlib_paths = [
            "lib/python",
            "Lib\\",
            "/usr/lib/python",
            "/usr/local/lib/python",
        ]

        origin = str(spec.origin) if spec.origin else ""
        return any(path in origin for path in stdlib_paths)

    except (ImportError, ValueError, AttributeError):
        return False


def _get_file_imports(file_path: Path) -> set[str]:
    """获取文件中的导入"""
    imports = set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

    except Exception as e:
        print(e)

    return imports


class ZipPackager:
    """将模块化项目打包成 ZIP 文件的工具"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.included_files: set[Path] = set()
        self.dependencies: dict[str, set[str]] = {}
        self.metadata = {
            "entry_point": None,
            "modules": {},
            "dependencies": {},
            "version": "1.0.0",
            "description": "Modular Python Application",
        }

    def add_module(
        self, module_path: str, module_name: str = None, recursive: bool = True
    ):
        """添加模块到包中"""
        module_path = Path(module_path)

        if not module_path.exists():
            raise FileNotFoundError(f"模块路径不存在: {module_path}")

        # 确定模块名
        if module_name is None:
            module_name = (
                module_path.stem if module_path.is_file() else module_path.name
            )

        if module_path.is_file():
            self._add_file(module_path, module_name)
        else:
            self._add_directory(module_path, module_name, recursive)

        # 分析依赖
        if recursive:
            self._analyze_dependencies(module_path, module_name)

    def _add_file(self, file_path: Path, module_name: str):
        """添加单个文件"""
        if file_path.suffix == ".py":
            self.included_files.add(file_path)
            self.metadata["modules"][module_name] = {
                "type": "file",
                "path": str(file_path.relative_to(self.project_root)),
                "entry": f"{module_name}.py",
            }

    def _add_directory(self, dir_path: Path, module_name: str, recursive: bool):
        """添加目录"""

        if recursive:
            python_files = list(dir_path.rglob("*.py"))
        else:
            python_files = list(dir_path.glob("*.py"))

        for py_file in python_files:
            self.included_files.add(py_file)

        # 检查是否是包（有 __init__.py）
        init_file = dir_path / "__init__.py"
        entry_point = "__init__.py" if init_file.exists() else None

        self.metadata["modules"][module_name] = {
            "type": "package",
            "path": str(dir_path.relative_to(self.project_root)),
            "entry": entry_point,
            "files": [str(f.relative_to(self.project_root)) for f in python_files],
        }

    def _analyze_dependencies(self, module_path: Path, module_name: str):
        """分析模块依赖"""
        deps = set()

        if module_path.is_file():
            deps.update(_get_file_imports(module_path))
        else:
            for py_file in module_path.rglob("*.py"):
                deps.update(_get_file_imports(py_file))

        # 过滤掉标准库和已包含的模块
        filtered_deps = set()
        for dep in deps:
            if not _is_stdlib(dep) and dep not in self.metadata["modules"]:
                filtered_deps.add(dep)

        if filtered_deps:
            self.dependencies[module_name] = filtered_deps
            self.metadata["dependencies"][module_name] = list(filtered_deps)

    def set_entry_point(self, entry_file: str):
        """设置入口文件"""
        entry_path = Path(entry_file)
        if not entry_path.exists():
            raise FileNotFoundError(f"入口文件不存在: {entry_path}")

        self.metadata["entry_point"] = str(entry_path.relative_to(self.project_root))

    def add_resource_files(self, resource_patterns: list[str]):
        """添加资源文件"""
        for pattern in resource_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    self.included_files.add(file_path)

    def create_package(self, output_path: str, include_metadata: bool = True) -> str:
        """创建 ZIP 包"""
        output_path = Path(output_path)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有包含的文件
            for file_path in self.included_files:
                # 计算在 ZIP 中的路径
                arc_name = str(file_path.relative_to(self.project_root))
                zipf.write(file_path, arc_name)

            # 添加元数据
            if include_metadata:
                metadata_json = json.dumps(self.metadata, indent=2, ensure_ascii=False)
                zipf.writestr("__package_metadata__.json", metadata_json)

            # 创建 __main__.py（如果有入口点）
            if self.metadata["entry_point"]:
                main_py_content = self._create_main_py()
                zipf.writestr("__main__.py", main_py_content)

        return str(output_path)

    def _create_main_py(self) -> str:
        """创建 __main__.py 文件"""
        entry_point = self.metadata["entry_point"]

        # 去掉 .py 后缀并转换为模块路径
        module_path = (
            entry_point.replace(".py", "").replace("/", ".").replace("\\", ".")
        )

        return f"""import sys
import os
from pathlib import Path

# 添加当前 ZIP 包到 Python 路径
current_zip = Path(__file__).parent
if str(current_zip) not in sys.path:
    sys.path.insert(0, str(current_zip))

# 导入并运行主模块
if __name__ == "__main__":
    try:
        # 尝试导入主模块
        import {module_path} as main_module

        # 如果有 main 函数就调用
        if hasattr(main_module, 'main'):
            main_module.main()
        elif hasattr(main_module, '__main__'):
            # 执行 __main__ 块的内容
            pass
        else:
            print("⚠️ 主模块没有找到 main() 函数")

    except ImportError as e:
        print(f"❌ 导入主模块失败: {{e}}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {{e}}")
        sys.exit(1)
"""


class ZipProjectPackager:
    """zip 项目级打包器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.packager = ZipPackager(project_root)

    def package_project(self, project_config: ZipExampleConfig):
        """根据配置打包项目"""

        # 添加模块
        for module_config in project_config.get("modules", []):
            self.packager.add_module(
                module_config["path"],
                module_config.get("name"),
                module_config.get("recursive", True),
            )

        # 设置入口点
        if "entry_point" in project_config:
            self.packager.set_entry_point(project_config["entry_point"])

        # 添加资源文件
        if "resources" in project_config:
            self.packager.add_resource_files(project_config["resources"])

        # 设置元数据
        for key in ["version", "description"]:
            if key in project_config:
                self.packager.metadata[key] = project_config[key]

        # 创建包
        output_path = project_config.get("output", "dist/app.zip")
        return self.packager.create_package(output_path)


__all__ = ["ZipPackager", "ZipProjectPackager"]
