# brainary/capabilities/planning/adaptive_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class AdaptivePlanning(Planning):
    NAME = "Adaptive Planning"
    DESC = (
        "Dynamically adjusts plans in response to changing conditions, feedback, or unexpected events. "
        "Suitable for environments with uncertainty or evolving requirements, such as agile project management, "
        "robotics navigation in dynamic environments, or adaptive workflows. "
        "The plan can be revised iteratively to improve outcomes or handle constraints."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates an initial adaptive plan for the given task.
        """
        prompt = (
            "You are an expert adaptive planner.\n\n"
            "Given the task, generate a plan that can adapt to changes or unexpected conditions. "
            "Include contingency steps or flexible subtasks where possible.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Output the plan in bullet points or numbered steps.\n"
            "- Highlight potential contingencies or adaptive choices.\n"
            "- Do not include explanations or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Revises the plan based on feedback or new information.
        """
        prompt = (
            "You are an expert adaptive planner.\n\n"
            "Revise the plan below based on the feedback or changed conditions.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Provide an updated plan reflecting the feedback or changes.\n"
            "- Maintain adaptive flexibility and contingency steps.\n"
            "- Do not include explanations or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
