from typing import Literal


class ToolParameterSchema:
    def __init__(
        self, name: str, param_type: Literal["string", "number"], description: str
    ):
        self.name = name
        self.type = (
            str if param_type == "string" else int if param_type == "number" else None
        )
        self.description = description


class ToolSchema:
    def __init__(
        self, name: str, description: str, parameters: list[ToolParameterSchema]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters


class ToolUrlSchema(ToolSchema):
    def __init__(
        self,
        name: str,
        url: str,
        description: str,
        parameters: list[ToolParameterSchema],
    ):
        super().__init__(name, description, parameters)
        self.url = url


__all__ = ["ToolSchema", "ToolUrlSchema", "ToolParameterSchema"]
