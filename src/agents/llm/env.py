"""Environment helpers for model backend selection."""
import os


def get_default_model_backend() -> str:
    return os.getenv("LEARNWISE_LLM_BACKEND", "local_vllm")
