from typing import Literal

from pydantic import BaseModel


class ToolParameterSchema(BaseModel):
    """
    工具参数的模式定义类

    用于定义工具函数参数的结构和约束，包括参数名称、描述和类型信息。
    继承自 Pydantic 的 BaseModel，提供数据验证和序列化功能。
    """

    name: str
    """参数名称，用于标识参数的唯一标识符"""

    description: str
    """参数描述，说明参数的用途和含义"""

    param_type: Literal["string", "number"]
    """参数类型，限制为字符串类型或数字类型"""


class ToolSchema(BaseModel):
    """
    工具的基础模式定义类

    定义工具的基本结构，包括工具名称、描述和参数列表。
    作为其他具体工具类型的基类使用。
    """

    name: str
    """工具名称，用于标识工具的唯一标识符"""

    description: str
    """工具描述，说明工具的功能和用途"""

    parameters: list[ToolParameterSchema]
    """工具参数列表，包含该工具所需的所有参数定义"""


class ToolUrlSchema(ToolSchema):
    """
    URL 工具的模式定义类

    继承自 ToolSchema，专门用于定义基于 URL 的工具。
    在基础工具结构上增加了 URL 字段，用于指定工具的网络地址。
    """

    url: str
    """工具的 URL 地址，指定工具的网络访问地址"""


__all__ = ["ToolSchema", "ToolUrlSchema", "ToolParameterSchema"]
