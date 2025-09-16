# brainary/capabilities/planning/htn_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class HTNPlanning(Planning):
    NAME = "Hierarchical Task Network (HTN) Planning"
    DESC = (
        "Decompose complex instructions into a hierarchy of subtasks. "
        "Suitable for multi-step tasks that can be structured into ordered sub-goals, "
        "like project management, procedural workflows, or multi-step problem solving. "
        "HTN allows planning at different abstraction levels and can generate a stepwise plan "
        "from high-level goals down to executable actions."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a hierarchical decomposition of the task into subtasks.
        """
        prompt = (
            "You are an expert hierarchical task planner.\n\n"
            "Decompose the following task into a hierarchy of subtasks, "
            "starting from high-level goals to actionable sub-goals. "
            "Output as a nested list in plain text.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Represent subtasks using indentation or bullet points to show hierarchy.\n"
            "- Do not include explanations or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Revises the hierarchical plan based on feedback.
        """
        prompt = (
            "You are an expert hierarchical task planner.\n\n"
            "The previous plan might need adjustment based on feedback.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Provide an updated hierarchical plan reflecting the feedback.\n"
            "- Maintain the hierarchy structure.\n"
            "- Do not include explanations or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
