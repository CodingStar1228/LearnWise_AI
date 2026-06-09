# src/agents/agents/teacher.py
import os
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command

from ..base import State
from ..models import get_llm
from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "prompts")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
DS_INDICES_PATH = os.path.join(ROOT_DIR, "data", "ds_data", "ds_indices.pkl")


async def knowledge_summry_search(knowledge_points: list) -> str:
    """Fetch knowledge point summaries (Python-side, no model tool calling)."""
    try:
        system = await KnowledgeIndexSystem.load_indices_async(DS_INDICES_PATH)
        knowledge_summry = []
        for kp in knowledge_points:
            knowledge_point_info = await system.get_knowledge_point_async(kp)
            if knowledge_point_info:
                knowledge_summry.append({
                    "knowledge_point": knowledge_point_info["title"],
                    "summry": knowledge_point_info["summry"],
                })
        if knowledge_summry:
            return "\n".join([f"{kp['knowledge_point']}: {kp['summry']}" for kp in knowledge_summry])
        return "No matching knowledge points found."
    except Exception as e:
        return str(e)


class TeacherAgent:
    """教师智能体 — pre-fetches knowledge, then calls EasyEdu LLMClient."""

    def __init__(self, model_type: str = "local_vllm"):
        self.model_type = model_type

    async def __call__(self, state: State, config) -> Command[Literal["__end__"]]:
        try:
            curr_question = state.question[0]
            evaluation = state.evaluation

            prompt_path = os.path.join(PROMPTS_DIR, "teacher_agent_prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            knowledge_points = curr_question.get("knowledge_points", [])
            knowledge_context = ""
            if knowledge_points:
                knowledge_context = await knowledge_summry_search(knowledge_points)

            system_text = prompt_template.format(
                title=curr_question["title"],
                content=curr_question["content"],
                answer=curr_question["reference_answer"]["content"],
                knowledge_points=knowledge_points,
                explanation=curr_question["reference_answer"]["explanation"],
                is_right=evaluation.get("is_right"),
                is_complete=evaluation.get("is_complete"),
                reason=evaluation.get("reason", ""),
                knowledge_context=knowledge_context or "N/A",
            )

            messages = [SystemMessage(content=system_text)]
            messages.extend(state.messages)

            client = get_llm(model_type=self.model_type)
            content = await client.chat(messages)

            return Command(
                update={"messages": AIMessage(content=content)},
                goto="__end__",
            )

        except Exception as e:
            return Command(
                update={"log": str(e), "messages": AIMessage(content=f"Sorry, an error occurred: {e}")},
                goto="__end__",
            )
