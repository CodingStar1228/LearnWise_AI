# src/agents/models.py — LearnWise_AI model factory (default: self-hosted vLLM)
from src.agents.llm.client import LLMClient, get_client


def get_llm(model_type: str = "local_vllm", **kwargs) -> LLMClient:
    """
    Return LearnWise_AI LLM client. Default backend is local_vllm (self-hosted).
    Fallback aliases for dev: deepseek, tongyi, qwen2.5.
    """
    return get_client(model_type=model_type)
