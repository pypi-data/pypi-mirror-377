from abc import ABC, abstractmethod
from datetime import datetime
from typing import Literal, Any, Sequence
from uuid import uuid4, UUID

import tiktoken
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler, AsyncCallbackHandler
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk, LLMResult
from tenacity import RetryCallState


class MonitorCore(BaseCallbackHandler, ABC):
    """LangChain 组件监控抽象基类，提供标准化的日志记录和监控功能。

    该类定义了监控 LangChain 各组件（LLM、Chain、Tool）执行过程的标准接口，
    子类需实现 _db_operations 方法以完成日志数据的持久化存储。
    """

    def __init__(
        self, thread_id: str | None = None, token_model_name: str = "gpt-3.5-turbo"
    ) -> None:
        """初始化监控器核心实例。

        Args:
            thread_id (str | None): 线程/协程标识符，用于区分不同执行上下文。
                                      如果未提供，则自动生成一个新的 UUID。
            token_model_name (str): 用于 token 计数的模型名称，默认为 "gpt-3.5-turbo"。
                                   必须与 tiktoken 支持的模型名称一致。
        """
        self.thread_id = thread_id or uuid4()
        self.token_encoder = tiktoken.encoding_for_model(token_model_name)

    def _count_tokens(self, text: str | list[BaseMessage]) -> int:
        """计算输入内容的 token 数量。

        支持普通字符串和 LangChain 的 BaseMessage 列表（用于聊天模型）。

        Args:
            text (str | list[BaseMessage]): 要计算的内容，可以是字符串或消息列表。

        Returns:
            int: 计算得出的 token 数量。如果输入为空或无效，返回 0。
        """
        if isinstance(text, str):
            return len(self.token_encoder.encode(text))
        elif isinstance(text, list):
            return sum(
                len(self.token_encoder.encode(msg.content))
                for msg in text
                if hasattr(msg, "content")
            )
        return 0

    def _prepare_log_data(
        self,
        run_id: UUID,
        parent_run_id: UUID | None,
        event_type: Literal[
            "llm",
            "llm_error",
            "chat_model",
            "token",
            "chain",
            "chain_error",
            "tool",
            "tool_error",
            "text",
            "agent",
            "retriever",
            "retriever_error",
            "custom",
        ],
        event_name: str,
        input_data: Any,
        output_data: Any,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """构造标准化的日志数据结构。

        将监控数据转换为统一的字典格式，包含 trace_id、时间戳、token 用量等标准字段。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            event_type (Literal): 事件类型标识，限定为预定义的几种组件类型。
            event_name (str): 组件名称（如模型名称、工具名称等）。
            input_data (Any): 输入数据，会自动转换为字符串格式。
            output_data (Any): 输出数据，会自动转换为字符串格式。
            tags (list[str] | None): 相关标签列表。如果为 None 则使用空列表。
            metadata (dict | None): 附加的元数据字典。如果为 None 则使用空字典。
            **kwargs: 其他运行时参数。

        Returns:
            dict[str, Any]: 标准化的日志数据字典。
        该字典包含以下字段：
            - trace_id: 唯一的日志条目标识符（UUID）。
            - run_id: 当前运行的唯一标识符（UUID）。
            - thread_id: 线程/协程标识符。
            - parent_run_id: 父运行的唯一标识符（UUID 或 None）。
            - event_type: 事件类型（如 "llm"、"chain"、"tool" 及其错误变体）。
            - event_name: 组件名称（如模型名称、工具名称等）。
            - input_data: 输入数据的字符串表示。
            - output_data: 输出数据的字符串表示。
            - timestamp: 事件发生的时间戳（ISO 格式字符串）。
            - token_usage: 输入和输出数据的总 token 数量。
            - tags: 相关标签列表。
            - metadata: 附加的元数据字典。
            - kwargs: 其他运行时参数。

        """
        metadata = metadata or {}
        return {
            "trace_id": uuid4(),
            "run_id": run_id,
            "thread_id": self.thread_id,
            "parent_run_id": parent_run_id,
            "event_type": event_type,
            "event_name": event_name,
            "input_data": str(input_data),
            "output_data": str(output_data),
            "timestamp": datetime.now().isoformat(),
            "token_usage": (
                self._count_tokens(input_data) + self._count_tokens(output_data)
            ),
            "tags": tags,
            "metadata": metadata,
            "kwargs": kwargs,
        }

    @abstractmethod
    def _db_operations(self, log_data: dict[str, Any]) -> None:
        """数据库操作抽象方法（必须由子类实现）。

        定义如何将标准化日志数据持久化到存储系统（如数据库、文件等）。

        Args:
            log_data (dict[str, Any]): 由 _prepare_log_data 生成的标准化日志字典。

        Raises:
            NotImplementedError: 如果子类没有实现该方法。
        """
        raise NotImplementedError("_db_operations must be implemented in subclasses")

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 开始处理时的回调方法。

        当语言模型开始处理输入提示时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含 LLM 配置的序列化字典。
            prompts (list[str]): 输入给 LLM 的提示列表。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm",
            event_name=serialized.get("name", "unknown_llm"),
            input_data=prompts,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """聊天模型开始处理时的回调方法。

        当聊天模型开始处理输入消息时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含聊天模型配置的序列化字典。
            messages (list[list[BaseMessage]]): 输入给聊天模型的消息列表。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chat_model",
            event_name=serialized.get("name", "unknown_chat_model"),
            input_data=messages,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: GenerationChunk | ChatGenerationChunk | None = None,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 生成新 token 时的回调方法。

        当语言模型生成新的 token 时会触发此方法。

        Args:
            token (str): 新生成的 token 字符串。
            chunk (GenerationChunk | ChatGenerationChunk | None): 可选的生成块信息。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="token",
            event_name=kwargs.get("name", "unknown_token"),
            input_data="",
            output_data=token,
            tags=tags,
            metadata={"chunk": str(chunk)} if chunk else None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 处理结束时的回调方法。

        当语言模型完成处理并返回结果时会触发此方法。

        Args:
            response (LLMResult): LLM 生成的结果对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm",
            event_name=kwargs.get("name", "unknown_llm"),
            input_data="",
            output_data=response,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 处理出错时的回调方法。

        当语言模型在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm_error",
            event_name=kwargs.get("name", "unknown_llm"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Chain 开始处理时的回调方法。

        当链式组件开始处理输入数据时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含 Chain 配置的序列化字典。
            inputs (dict[str, Any]): 输入给 Chain 的数据字典。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain",
            event_name=serialized.get("name", "unknown_chain"),
            input_data=inputs,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Chain 处理结束时的回调方法。

        当链式组件完成处理并返回结果时会触发此方法。

        Args:
            outputs (dict[str, Any]): Chain 生成的输出数据字典。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain",
            event_name=kwargs.get("name", "unknown_chain"),
            input_data="",
            output_data=outputs,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Chain 处理出错时的回调方法。

        当链式组件在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain_error",
            event_name=kwargs.get("name", "unknown_chain"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Tool 开始处理时的回调方法。

        当工具组件开始处理输入数据时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含 Tool 配置的序列化字典。
            input_str (str): 输入给 Tool 的字符串数据。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            inputs (dict[str, Any] | None): 可选的输入数据字典。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool",
            event_name=serialized.get("name", "unknown_tool"),
            input_data=input_str,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Tool 处理结束时的回调方法。

        当工具组件完成处理并返回结果时会触发此方法。

        Args:
            output (Any): Tool 生成的输出数据。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool",
            event_name=kwargs.get("name", "unknown_tool"),
            input_data="",
            output_data=output,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Tool 处理出错时的回调方法。

        当工具组件在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool_error",
            event_name=kwargs.get("name", "unknown_tool"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_text(
        self,
        text: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """文本输出时的回调方法。

        当组件输出文本内容时会触发此方法。

        Args:
            text (str): 输出的文本内容。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="text",
            event_name=kwargs.get("name", "unknown_text"),
            input_data="",
            output_data=text,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_retry(
        self,
        retry_state: RetryCallState,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """重试操作时的回调方法。

        当组件执行重试逻辑时会触发此方法。

        Args:
            retry_state (RetryCallState): 当前的重试状态对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="text",
            event_name=kwargs.get("name", "unknown_retry"),
            input_data="",
            output_data=str(retry_state),
            tags=None,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """代理动作执行时的回调方法。

        当代理组件执行某个动作时会触发此方法。

        Args:
            action (AgentAction): 当前的代理动作对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="agent",
            event_name=action.tool,
            input_data=action.tool_input,
            output_data="",
            tags=tags,
            metadata={"action": str(action)} if action else None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """代理完成执行时的回调方法。

        当代理组件完成所有动作并返回最终结果时会触发此方法。

        Args:
            finish (AgentFinish): 当前的代理完成对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="agent",
            event_name=kwargs.get("name", "unknown_agent"),
            input_data="",
            output_data=finish.return_values,
            tags=tags,
            metadata={"finish": str(finish)} if finish else None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """检索器开始处理时的回调方法。

        当检索器组件开始处理查询时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含检索器配置的序列化字典。
            query (str): 输入给检索器的查询字符串。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="retriever",
            event_name=serialized.get("name", "unknown_retriever"),
            input_data=query,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """检索器处理结束时的回调方法。

        当检索器组件完成处理并返回结果时会触发此方法。

        Args:
            documents (Sequence[Document]): 检索器返回的文档列表。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="retriever",
            event_name=kwargs.get("name", "unknown_retriever"),
            input_data="",
            output_data=documents,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """检索器处理出错时的回调方法。

        当检索器组件在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="retriever_error",
            event_name=kwargs.get("name", "unknown_retriever"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        self._db_operations(log_data)

    def on_custom_event(
        self,
        name: str,
        data: Any,
        *,
        run_id: UUID,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """自定义事件的回调方法。

        当需要记录非标准化事件时可以触发此方法。

        Args:
            name (str): 自定义事件的名称。
            data (Any): 事件相关的数据内容。
            run_id (UUID): 当前运行的唯一标识符。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=None,
            event_type="custom",
            event_name=name,
            input_data="",
            output_data=data,
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        self._db_operations(log_data)


class AsyncMonitorCore(AsyncCallbackHandler, ABC):
    """LangChain 组件监控异步抽象基类，提供标准化的日志记录和监控功能。

    该类定义了监控 LangChain 各组件（LLM、Chain、Tool）执行过程的标准接口，
    子类需实现 _db_operations 方法以完成日志数据的持久化存储。
    """

    def __init__(
        self, thread_id: str | None = None, token_model_name: str = "gpt-3.5-turbo"
    ) -> None:
        """初始化监控器核心实例。

        Args:
            thread_id (str | None): 线程/协程标识符，用于区分不同执行上下文。
                                      如果未提供，则自动生成一个新的 UUID。
            token_model_name (str): 用于 token 计数的模型名称，默认为 "gpt-3.5-turbo"。
                                   必须与 tiktoken 支持的模型名称一致。
        """
        self.thread_id = thread_id or uuid4()
        self.token_encoder = tiktoken.encoding_for_model(token_model_name)

    def _count_tokens(self, text: str | list[BaseMessage]) -> int:
        """计算输入内容的 token 数量。

        支持普通字符串和 LangChain 的 BaseMessage 列表（用于聊天模型）。

        Args:
            text (str | list[BaseMessage]): 要计算的内容，可以是字符串或消息列表。

        Returns:
            int: 计算得出的 token 数量。如果输入为空或无效，返回 0。
        """
        if isinstance(text, str):
            return len(self.token_encoder.encode(text))
        elif isinstance(text, list):
            return sum(
                len(self.token_encoder.encode(msg.content))
                for msg in text
                if hasattr(msg, "content")
            )
        return 0

    def _prepare_log_data(
        self,
        run_id: UUID,
        parent_run_id: UUID | None,
        event_type: Literal[
            "llm",
            "llm_error",
            "chat_model",
            "token",
            "chain",
            "chain_error",
            "tool",
            "tool_error",
            "text",
            "agent",
            "retriever",
            "retriever_error",
            "custom",
        ],
        event_name: str,
        input_data: Any,
        output_data: Any,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """构造标准化的日志数据结构。

        将监控数据转换为统一的字典格式，包含 trace_id、时间戳、token 用量等标准字段。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            event_type (Literal): 事件类型标识，限定为预定义的几种组件类型。
            event_name (str): 组件名称（如模型名称、工具名称等）。
            input_data (Any): 输入数据，会自动转换为字符串格式。
            output_data (Any): 输出数据，会自动转换为字符串格式。
            tags (list[str] | None): 相关标签列表。如果为 None 则使用空列表。
            metadata (dict | None): 附加的元数据字典。如果为 None 则使用空字典。
            **kwargs: 其他运行时参数。

        Returns:
            dict[str, Any]: 标准化的日志数据字典。
        该字典包含以下字段：
            - trace_id: 唯一的日志条目标识符（UUID）。
            - run_id: 当前运行的唯一标识符（UUID）。
            - thread_id: 线程/协程标识符。
            - parent_run_id: 父运行的唯一标识符（UUID 或 None）。
            - event_type: 事件类型（如 "llm"、"chain"、"tool" 及其错误变体）。
            - event_name: 组件名称（如模型名称、工具名称等）。
            - input_data: 输入数据的字符串表示。
            - output_data: 输出数据的字符串表示。
            - timestamp: 事件发生的时间戳（ISO 格式字符串）。
            - token_usage: 输入和输出数据的总 token 数量。
            - tags: 相关标签列表。
            - metadata: 附加的元数据字典。
            - kwargs: 其他运行时参数。

        """
        metadata = metadata or {}
        return {
            "trace_id": uuid4(),
            "run_id": run_id,
            "thread_id": self.thread_id,
            "parent_run_id": parent_run_id,
            "event_type": event_type,
            "event_name": event_name,
            "input_data": str(input_data),
            "output_data": str(output_data),
            "timestamp": datetime.now().isoformat(),
            "token_usage": (
                self._count_tokens(input_data) + self._count_tokens(output_data)
            ),
            "tags": tags,
            "metadata": metadata,
            "kwargs": kwargs,
        }

    @abstractmethod
    async def _db_operations(self, log_data: dict[str, Any]) -> None:
        """数据库操作抽象方法（必须由子类实现）。

        定义如何将标准化日志数据持久化到存储系统（如数据库、文件等）。

        Args:
            log_data (dict[str, Any]): 由 _prepare_log_data 生成的标准化日志字典。

        Raises:
            NotImplementedError: 如果子类没有实现该方法。
        """
        raise NotImplementedError("_db_operations must be implemented in subclasses")

    async def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 开始处理时的回调方法。

        当语言模型开始处理输入提示时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含 LLM 配置的序列化字典。
            prompts (list[str]): 输入给 LLM 的提示列表。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm",
            event_name=serialized.get("name", "unknown_llm"),
            input_data=prompts,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """聊天模型开始处理时的回调方法。

        当聊天模型开始处理输入消息时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含聊天模型配置的序列化字典。
            messages (list[list[BaseMessage]]): 输入给聊天模型的消息列表。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chat_model",
            event_name=serialized.get("name", "unknown_chat_model"),
            input_data=messages,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: GenerationChunk | ChatGenerationChunk | None = None,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 生成新 token 时的回调方法。

        当语言模型生成新的 token 时会触发此方法。

        Args:
            token (str): 新生成的 token 字符串。
            chunk (GenerationChunk | ChatGenerationChunk | None): 可选的生成块信息。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="token",
            event_name=kwargs.get("name", "unknown_token"),
            input_data="",
            output_data=token,
            tags=tags,
            metadata={"chunk": str(chunk)} if chunk else None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 处理结束时的回调方法。

        当语言模型完成处理并返回结果时会触发此方法。

        Args:
            response (LLMResult): LLM 生成的结果对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm",
            event_name=kwargs.get("name", "unknown_llm"),
            input_data="",
            output_data=response,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 处理出错时的回调方法。

        当语言模型在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm_error",
            event_name=kwargs.get("name", "unknown_llm"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Chain 开始处理时的回调方法。

        当链式组件开始处理输入数据时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含 Chain 配置的序列化字典。
            inputs (dict[str, Any]): 输入给 Chain 的数据字典。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain",
            event_name=serialized.get("name", "unknown_chain"),
            input_data=inputs,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Chain 处理结束时的回调方法。

        当链式组件完成处理并返回结果时会触发此方法。

        Args:
            outputs (dict[str, Any]): Chain 生成的输出数据字典。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain",
            event_name=kwargs.get("name", "unknown_chain"),
            input_data="",
            output_data=outputs,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Chain 处理出错时的回调方法。

        当链式组件在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain_error",
            event_name=kwargs.get("name", "unknown_chain"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Tool 开始处理时的回调方法。

        当工具组件开始处理输入数据时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含 Tool 配置的序列化字典。
            input_str (str): 输入给 Tool 的字符串数据。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            inputs (dict[str, Any] | None): 可选的输入数据字典。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool",
            event_name=serialized.get("name", "unknown_tool"),
            input_data=input_str,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Tool 处理结束时的回调方法。

        当工具组件完成处理并返回结果时会触发此方法。

        Args:
            output (Any): Tool 生成的输出数据。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool",
            event_name=kwargs.get("name", "unknown_tool"),
            input_data="",
            output_data=output,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Tool 处理出错时的回调方法。

        当工具组件在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool_error",
            event_name=kwargs.get("name", "unknown_tool"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_text(
        self,
        text: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """文本输出时的回调方法。

        当组件输出文本内容时会触发此方法。

        Args:
            text (str): 输出的文本内容。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="text",
            event_name=kwargs.get("name", "unknown_text"),
            input_data="",
            output_data=text,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_retry(
        self,
        retry_state: RetryCallState,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """重试操作时的回调方法。

        当组件执行重试逻辑时会触发此方法。

        Args:
            retry_state (RetryCallState): 当前的重试状态对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="text",
            event_name=kwargs.get("name", "unknown_retry"),
            input_data="",
            output_data=str(retry_state),
            tags=None,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """代理动作执行时的回调方法。

        当代理组件执行某个动作时会触发此方法。

        Args:
            action (AgentAction): 当前的代理动作对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="agent",
            event_name=action.tool,
            input_data=action.tool_input,
            output_data="",
            tags=tags,
            metadata={"action": str(action)} if action else None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """代理完成执行时的回调方法。

        当代理组件完成所有动作并返回最终结果时会触发此方法。

        Args:
            finish (AgentFinish): 当前的代理完成对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="agent",
            event_name=kwargs.get("name", "unknown_agent"),
            input_data="",
            output_data=finish.return_values,
            tags=tags,
            metadata={"finish": str(finish)} if finish else None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """检索器开始处理时的回调方法。

        当检索器组件开始处理查询时会触发此方法。

        Args:
            serialized (dict[str, Any]): 包含检索器配置的序列化字典。
            query (str): 输入给检索器的查询字符串。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="retriever",
            event_name=serialized.get("name", "unknown_retriever"),
            input_data=query,
            output_data="",
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """检索器处理结束时的回调方法。

        当检索器组件完成处理并返回结果时会触发此方法。

        Args:
            documents (Sequence[Document]): 检索器返回的文档列表。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="retriever",
            event_name=kwargs.get("name", "unknown_retriever"),
            input_data="",
            output_data=documents,
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """检索器处理出错时的回调方法。

        当检索器组件在处理过程中发生错误时会触发此方法。

        Args:
            error (BaseException): 捕获的异常对象。
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="retriever_error",
            event_name=kwargs.get("name", "unknown_retriever"),
            input_data="",
            output_data=str(error),
            tags=tags,
            metadata=None,
            **kwargs,
        )
        await self._db_operations(log_data)

    async def on_custom_event(
        self,
        name: str,
        data: Any,
        *,
        run_id: UUID,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """自定义事件的回调方法。

        当需要记录非标准化事件时可以触发此方法。

        Args:
            name (str): 自定义事件的名称。
            data (Any): 事件相关的数据内容。
            run_id (UUID): 当前运行的唯一标识符。
            tags (list[str] | None): 相关标签列表，如果没有则为 None。
            metadata (dict[str, Any] | None): 附加的元数据字典
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=None,
            event_type="custom",
            event_name=name,
            input_data="",
            output_data=data,
            tags=tags,
            metadata=metadata,
            **kwargs,
        )
        await self._db_operations(log_data)


__all__ = ["MonitorCore", "AsyncMonitorCore"]
