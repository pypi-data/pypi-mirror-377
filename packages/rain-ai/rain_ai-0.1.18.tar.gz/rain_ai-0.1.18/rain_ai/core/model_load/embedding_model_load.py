from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr


def load_open_ai_api_embedding_model(
    base_url: str,
    api_key: str,
    model_name: str,
    dimensions: int = 1024,
    timeout: float | None = None,
    max_retries: int | None = None,
    check_embedding_ctx_length: bool | None = False,
) -> Embeddings:
    """
    加载OpenAI API的嵌入模型

    此函数创建并返回一个OpenAIEmbeddings实例，用于生成文本嵌入向量

    Args:
        base_url (str): OpenAI API的基础URL，可以是官方API或兼容API的端点
        api_key (str): 用于认证的API密钥
        model_name (str): 要使用的嵌入模型名称，例如'text-embedding-ada-002'
        dimensions (int, 可选): 嵌入向量的维度，默认为1024
        timeout (float, 可选): API请求的超时时间(秒)，None表示使用默认值
        max_retries (int, 可选): 请求失败时的最大重试次数，None表示使用默认值
        check_embedding_ctx_length (bool, 可选): 是否检查嵌入上下文长度，默认为False, 如果为True，将在嵌入前检查文本长度是否超过模型的上下文限制，使用这个配置模型的input必须支持数据类型是 token id 数组

    Returns:
        Embeddings: 配置好的OpenAIEmbeddings实例，可用于生成文本嵌入
    """
    return OpenAIEmbeddings(
        base_url=base_url,
        api_key=SecretStr(api_key),
        model=model_name,
        dimensions=dimensions,
        timeout=timeout,
        max_retries=max_retries,
        check_embedding_ctx_length=check_embedding_ctx_length,
    )


def load_ollama_api_embedding_model(
    base_url: str,
    model_name: str,
) -> Embeddings:
    """
     加载Ollama服务的嵌入模型

     此函数创建并返回一个OllamaEmbeddings实例，用于通过本地运行的Ollama服务，生成文本嵌入向量

    Args:
        base_url (str): Ollama服务的基础URL，通常是本地运行的Ollama实例地址
        model_name (str): 要使用的嵌入模型名称，例如'text-embedding-ada-002'

     Returns:
         Embeddings: 配置好的OllamaEmbeddings实例，可用于生成文本嵌入
    """
    return OllamaEmbeddings(
        base_url=base_url,
        model=model_name,
    )


__all__ = [
    "load_open_ai_api_embedding_model",
    "load_ollama_api_embedding_model",
]
