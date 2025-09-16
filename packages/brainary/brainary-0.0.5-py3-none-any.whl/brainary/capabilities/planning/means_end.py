# brainary/capabilities/planning/means_end_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class MeansEndPlanning(Planning):
    NAME = "Means-End Planning"
    DESC = (
        "Decomposes a complex goal into sub-goals (ends) and identifies actions (means) "
        "to achieve each sub-goal. Useful when the overall goal is complex or multi-step, "
        "such as strategic problem solving, project planning, or multi-stage tasks."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a plan by breaking the goal into sub-goals and identifying actions for each.
        """
        prompt = (
            "You are an expert planner using the Means-End strategy.\n\n"
            "Given the task, generate a plan that:\n"
            "- Identifies the main goal.\n"
            "- Breaks it into sub-goals (ends).\n"
            "- For each sub-goal, lists actions (means) required to achieve it.\n"
            "- Presents steps in logical order.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Use numbered or bullet points for clarity.\n"
            "- Ensure each action clearly connects to a sub-goal.\n"
            "- Do not include explanations, comments, or extra content."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Adjusts the plan based on feedback or changes in goals or constraints.
        """
        prompt = (
            "You are an expert planner using the Means-End strategy.\n\n"
            "The initial plan needs adjustment due to new feedback or constraints.\n"
            "Update the plan by reconsidering sub-goals and corresponding actions.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Preserve logical structure of sub-goals and actions.\n"
            "- Use bullet points or numbered steps.\n"
            "- Do not include explanations, comments, or extra content."
        )
        response = self.llm.request([prompt]).strip()
        return response
