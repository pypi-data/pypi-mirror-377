# brainary/capabilities/planning/backward_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class BackwardPlanning(Planning):
    NAME = "Backward Planning"
    DESC = (
        "Also known as goal-driven planning. This strategy starts from the desired goal and works backward "
        "to determine the necessary preconditions and actions to reach the goal. "
        "It is suitable for structured tasks where the goal is clearly defined, "
        "such as automated theorem proving, puzzle solving, or deterministic problem-solving environments. "
        "Helps identify dependencies and sequence actions efficiently."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a plan by reasoning backward from the goal.
        """
        prompt = (
            "You are an expert goal-driven planner.\n\n"
            "Given the goal described in the task, plan the necessary steps by working backward from the goal "
            "to the initial state. Identify required preconditions for each step.\n\n"
            f"## Task (Goal)\n{task}\n\n"
            "## Output Constraints\n"
            "- Output the steps in reverse order starting from the goal.\n"
            "- Provide each step clearly with necessary preconditions.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Revises the backward plan based on feedback or constraints.
        """
        prompt = (
            "You are an expert goal-driven planner.\n\n"
            "The initial plan needs revision based on the feedback or changes. "
            "Update the backward plan to account for the feedback, while maintaining goal-oriented reasoning.\n\n"
            f"## Task (Goal)\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Update the steps accordingly.\n"
            "- Preserve goal-driven reasoning and clear preconditions.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
