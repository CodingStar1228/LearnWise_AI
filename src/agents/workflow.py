# src/agents/workflow.py
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from .base import State
from .agents.router import RouterAgent
from .agents.student import StudentAgent
from .agents.teacher import TeacherAgent


def create_workflow(
    router_model_type: str = "local_vllm",
    teacher_model_type: str = "local_vllm",
    student_model_type: str = "local_vllm",
):
    """
    Create LangGraph workflow (orchestration only; models via LearnWise_AI LLMClient).

    Args:
        router_model_type: Model backend for router agent
        teacher_model_type: Model backend for teacher agent
        student_model_type: Model backend for student agent
    """
    workflow = StateGraph(State)

    router_agent = RouterAgent(model_type=router_model_type)
    student_agent = StudentAgent(model_type=student_model_type)
    teacher_agent = TeacherAgent(model_type=teacher_model_type)

    workflow.add_node("router_agent", router_agent)
    workflow.add_node("student_agent", student_agent)
    workflow.add_node("teacher_agent", teacher_agent)

    workflow.add_edge(START, "router_agent")
    workflow.add_edge("student_agent", "__end__")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
