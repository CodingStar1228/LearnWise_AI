# 模型工厂。默认给一个连本地 vLLM 的客户端；开发时也能切到 deepseek/tongyi 兜底。
from src.agents.llm.client import LLMClient, get_client


def get_llm(model_type: str = "local_vllm", **kwargs) -> LLMClient:
    return get_client(model_type=model_type)
