# brainary/capabilities/planning/critical_path_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class CriticalPathPlanning(Planning):
    NAME = "Critical Path Planning"
    DESC = (
        "Identifies the sequence of crucial steps (critical path) that determines the minimum completion time for a project or task. "
        "Useful in project management, workflow optimization, scheduling, and time-sensitive operations. "
        "Ensures resources are focused on steps that have the highest impact on timely completion."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a plan highlighting the critical path steps and dependencies.
        """
        prompt = (
            "You are an expert in project management and critical path analysis.\n\n"
            "Given the task, generate a detailed plan that:\n"
            "- Identifies all steps required to complete the task.\n"
            "- Highlights the critical path (steps that directly impact completion time).\n"
            "- Shows dependencies between steps.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Use bullet points or numbered steps.\n"
            "- Clearly indicate which steps are on the critical path.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Revises the critical path plan based on feedback or new constraints.
        """
        prompt = (
            "You are an expert in project management and critical path analysis.\n\n"
            "The initial plan needs adjustment based on new feedback or changes in resources/dependencies. "
            "Update the plan accordingly, highlighting the revised critical path.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Maintain a clear critical path.\n"
            "- Preserve logical dependencies.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
