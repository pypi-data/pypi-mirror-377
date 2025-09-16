# brainary/capabilities/planning/contingency_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class ContingencyPlanning(Planning):
    NAME = "Contingency Planning"
    DESC = (
        "Generates a primary plan along with fallback actions to handle failures or unexpected events. "
        "Useful in uncertain or high-risk environments where the main plan might not succeed. "
        "Applications include disaster response, critical operations, robotics, and adaptive workflow management. "
        "Ensures system robustness and minimizes risk by preparing alternative courses of action."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a plan with contingencies for possible failures or deviations.
        """
        prompt = (
            "You are an expert contingency planner.\n\n"
            "Given the task, generate a plan that includes:\n"
            "- A primary plan for the task.\n"
            "- Contingency actions in case the primary plan fails or unexpected events occur.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Clearly separate main plan and contingency plan.\n"
            "- Use bullet points or numbered steps.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Revises the contingency plan based on new feedback or observed issues.
        """
        prompt = (
            "You are an expert contingency planner.\n\n"
            "The initial plan requires revision due to new feedback or unexpected outcomes. "
            "Update the primary and contingency plans accordingly.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Maintain both primary and contingency plans.\n"
            "- Ensure logical consistency and robustness.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
