"""LearnWise_AI LLM configuration — env-driven, default local vLLM."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    backend: str
    base_url: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    timeout: float
    max_retries: int


def get_llm_config(model_type: str | None = None) -> LLMConfig:
    """
    Resolve LLM config for a model_type alias.
    Default backend: local_vllm (self-hosted OpenAI-compatible server).
    Fallback aliases: deepseek, tongyi, qwen2.5 (dev only).
    """
    backend = model_type or os.getenv("LEARNWISE_LLM_BACKEND", "local_vllm")

    defaults = {
        "temperature": float(os.getenv("LEARNWISE_LLM_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("LEARNWISE_LLM_MAX_TOKENS", "4096")),
        "timeout": float(os.getenv("LEARNWISE_LLM_TIMEOUT", "120")),
        "max_retries": int(os.getenv("LEARNWISE_LLM_MAX_RETRIES", "2")),
    }

    if backend == "local_vllm":
        return LLMConfig(
            backend="local_vllm",
            base_url=os.getenv("LEARNWISE_LLM_BASE_URL", "http://127.0.0.1:8000/v1"),
            api_key=os.getenv("LEARNWISE_LLM_API_KEY", "EMPTY"),
            model=os.getenv("LEARNWISE_LLM_MODEL", "Qwen2.5-7B-Instruct"),
            **defaults,
        )
    if backend == "deepseek":
        return LLMConfig(
            backend="deepseek",
            base_url="https://api.deepseek.com/v1",
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            **defaults,
        )
    if backend == "tongyi":
        return LLMConfig(
            backend="tongyi",
            base_url=os.getenv("TONGYI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            api_key=os.getenv("TONGYI_API_KEY", ""),
            model=os.getenv("TONGYI_MODEL", "qwen-plus"),
            **defaults,
        )
    if backend == "qwen2.5":
        return LLMConfig(
            backend="qwen2.5",
            base_url=os.getenv("LEARNWISE_LLM_BASE_URL", "http://127.0.0.1:8000/v1"),
            api_key=os.getenv("LEARNWISE_LLM_API_KEY", "EMPTY"),
            model=os.getenv("LEARNWISE_LLM_MODEL", "Qwen2.5-7B-Instruct"),
            **defaults,
        )

    raise ValueError(
        f"Unsupported model_type/backend: {backend}. "
        "Use local_vllm, deepseek, tongyi, or qwen2.5."
    )
