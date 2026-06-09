# src/agents/agents/student.py
import os

from langchain_core.messages import AIMessage, SystemMessage

from ..base import State
from ..models import get_llm

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "prompts")


class StudentAgent:
    """学生智能体 — Socratic peer learner via EasyEdu LLMClient."""

    def __init__(self, model_type: str = "local_vllm"):
        self.model_type = model_type

    async def __call__(self, state: State, config) -> dict:
        try:
            curr_question = state.question[0]
            evaluation = state.evaluation

            prompt_path = os.path.join(PROMPTS_DIR, "student_agent_prompt2.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            system_text = prompt_template.format(
                title=curr_question["title"],
                content=curr_question["content"],
                answer=curr_question["reference_answer"]["content"],
                explanation=curr_question["reference_answer"]["explanation"],
                is_right=evaluation.get("is_right"),
                is_complete=evaluation.get("is_complete"),
                reason=evaluation.get("reason", ""),
            )

            messages = [SystemMessage(content=system_text)]
            messages.extend(state.messages)

            client = get_llm(model_type=self.model_type)
            content = await client.chat(messages)

            return {"messages": AIMessage(content=content)}

        except Exception as e:
            return {"log": str(e), "messages": AIMessage(content=f"Sorry, an error occurred: {e}")}
