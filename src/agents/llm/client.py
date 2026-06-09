"""LearnWise_AI-owned LLM client — OpenAI-compatible HTTP, no LangChain model wrappers."""
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from .config import LLMConfig, get_llm_config
from .json_utils import parse_and_validate

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def messages_to_api(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    """Convert LangChain messages to OpenAI chat format."""
    out: List[Dict[str, str]] = []
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append({"role": "user", "content": str(m.content)})
        elif isinstance(m, AIMessage):
            out.append({"role": "assistant", "content": str(m.content)})
        elif isinstance(m, SystemMessage):
            out.append({"role": "system", "content": str(m.content)})
        elif hasattr(m, "type") and m.type == "human":
            out.append({"role": "user", "content": str(m.content)})
        elif hasattr(m, "type") and m.type == "ai":
            out.append({"role": "assistant", "content": str(m.content)})
        else:
            out.append({"role": "user", "content": str(m.content)})
    return out


class LLMClient:
    """Async client for self-hosted or fallback commercial LLM APIs."""

    def __init__(self, config: Optional[LLMConfig] = None, model_type: Optional[str] = None):
        self.config = config or get_llm_config(model_type)

    async def chat(
        self,
        messages: List[Dict[str, str]] | List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        if messages and isinstance(messages[0], BaseMessage):
            api_messages = messages_to_api(messages)
        else:
            api_messages = messages

        payload = {
            "model": self.config.model,
            "messages": api_messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
        }

        data = await self._post_chat(payload)
        return self._extract_content(data)

    async def chat_json(
        self,
        messages: List[Dict[str, str]] | List[BaseMessage],
        schema_model: Type[T],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> T:
        """Request JSON output; retry once with a stricter reminder on parse failure."""
        if messages and isinstance(messages[0], BaseMessage):
            api_messages = messages_to_api(messages)
        else:
            api_messages = list(messages)

        text = await self.chat(api_messages, temperature=temperature, max_tokens=max_tokens)
        parsed = parse_and_validate(text, schema_model)
        if parsed is not None:
            return parsed

        logger.warning("JSON parse failed, retrying with strict JSON reminder")
        retry_messages = api_messages + [
            {
                "role": "user",
                "content": (
                    "Your previous response was not valid JSON. "
                    "Reply with ONLY a single JSON object matching the required schema. "
                    "No markdown, no explanation."
                ),
            }
        ]
        text2 = await self.chat(retry_messages, temperature=0.3, max_tokens=max_tokens)
        parsed2 = parse_and_validate(text2, schema_model)
        if parsed2 is not None:
            return parsed2

        raise ValueError(
            f"Failed to parse JSON from model output. Last response: {text2[:500]}"
        )

    async def _post_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        last_err: Optional[Exception] = None
        for attempt in range(self.config.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_err = e
                logger.warning("LLM request attempt %s failed: %s", attempt + 1, e)
        raise RuntimeError(f"LLM request failed after retries: {last_err}")

    def _extract_content(self, data: Dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"Empty choices in LLM response: {data}")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if content is None:
            raise RuntimeError(f"No content in LLM response: {data}")
        return str(content).strip()


def get_client(model_type: Optional[str] = None) -> LLMClient:
    """Factory for LearnWise_AI LLM client."""
    return LLMClient(model_type=model_type)
