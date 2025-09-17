import inspect
from typing import Annotated

import httpx

from rain_ai.core.tool.decorator import tool_method
from rain_ai.core.tool.schemas import ToolUrlSchema


def make_url_tool_function(tool: ToolUrlSchema) -> tool_method:
    """
    根据 ToolUrlSchema 创建一个函数，该函数使用 HTTP GET 请求调用指定的 URL，并将工具参数作为查询参数传递

    Args:
        tool: ToolUrlSchema 实例，包含工具的名称、描述、URL 和参数信息

    Returns:
        一个函数，接受工具参数并返回 HTTP GET 请求的响应文本
    """
    # 构造参数名、类型和注解
    params = []
    for p in tool.parameters:
        annotated = Annotated[p.type, p.description]
        param = inspect.Parameter(
            name=p.name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=annotated,
        )
        params.append(param)

    # 构造函数签名
    sig = inspect.Signature(params, return_annotation=str)

    # 定义实际函数体
    param_names = [p.name for p in tool.parameters]

    def func(*args, **kwargs):
        if args:
            for i, value in enumerate(args):
                if i < len(param_names):
                    kwargs[param_names[i]] = value
        return httpx.get(tool.url, params=kwargs).text

    # 绑定签名和注解
    func.__signature__ = sig
    func.__name__ = tool.name

    return tool_method(func)


__all__ = ["make_url_tool_function"]
