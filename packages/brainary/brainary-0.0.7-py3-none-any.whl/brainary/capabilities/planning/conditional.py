# brainary/capabilities/planning/conditional_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class ConditionalPlanning(Planning):
    NAME = "Conditional Planning"
    DESC = (
        "This strategy produces plans that include branches based on possible outcomes or conditions. "
        "It is suitable for environments with uncertainty, incomplete information, or multiple possible scenarios. "
        "Typical applications include robotics, adaptive workflows, real-time decision-making, and planning under risk. "
        "The planner specifies if-then branches to handle contingencies."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a conditional plan that branches based on potential outcomes.
        """
        prompt = (
            "You are an expert conditional planner.\n\n"
            "Given the task, generate a plan that includes conditional branches "
            "to handle possible scenarios and uncertainties.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Use IF-THEN structure to describe branches.\n"
            "- Cover at least two possible scenarios.\n"
            "- Ensure each branch specifies clear actions.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Revises the conditional plan based on feedback or changes in the environment.
        """
        prompt = (
            "You are an expert conditional planner.\n\n"
            "The initial conditional plan needs revision based on new feedback or constraints. "
            "Update the plan while maintaining proper conditional branches.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Update IF-THEN branches accordingly.\n"
            "- Ensure logical consistency and adaptability to new conditions.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
