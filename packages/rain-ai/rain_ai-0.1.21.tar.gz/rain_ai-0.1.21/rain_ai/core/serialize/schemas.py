from pydantic import BaseModel


class ZipExampleModulesConfig(BaseModel):
    """
    Zip示例模块配置类

    定义需要打包到zip文件中的模块配置信息。
    """

    path: str
    """模块路径，指定需要打包的模块或目录的路径"""

    name: str
    """模块名称，用于标识模块的名称"""

    recursive: bool | None
    """是否递归打包，为True时递归包含子目录，None时使用默认设置"""


class ZipExampleConfig(BaseModel):
    """
    Zip示例配置类

    定义创建zip示例包的完整配置信息，包括模块列表、入口点、资源文件等。
    """

    modules: list[ZipExampleModulesConfig]
    """模块列表，包含所有需要打包的模块配置"""

    entry_point: str | None
    """入口点，指定程序的主入口文件或函数"""

    resources: list[str] | None
    """资源文件列表，包含需要打包的额外资源文件路径"""

    output: str
    """输出路径，指定生成的zip文件的输出位置"""

    version: str | None
    """版本号，标识示例包的版本信息"""

    description: str | None
    """描述信息，说明示例包的功能和用途"""


__all__ = ["ZipExampleModulesConfig", "ZipExampleConfig"]
