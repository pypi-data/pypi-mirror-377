# brainary/capabilities/planning/forward_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class ForwardPlanning(Planning):
    NAME = "Forward Planning"
    DESC = (
        "Generates a plan by starting from the initial state and incrementally applying actions "
        "to reach the goal. Useful in situations where the initial conditions are well-defined "
        "and the goal state is known, such as task execution, workflow automation, or stepwise problem solving."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a plan using forward-chaining reasoning from initial conditions to goal.
        """
        prompt = (
            "You are an expert planner using forward-chaining strategy.\n\n"
            "Given the task, generate a detailed plan that:\n"
            "- Starts from the initial state.\n"
            "- Incrementally applies actions to reach the goal state.\n"
            "- Lists steps in logical order.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Use numbered or bullet points.\n"
            "- Do not skip intermediate steps.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Adjusts the plan based on feedback or changed initial conditions.
        """
        prompt = (
            "You are an expert planner using forward-chaining strategy.\n\n"
            "The initial plan needs adjustment due to new feedback or changes in the initial state.\n"
            "Update the plan accordingly, ensuring each step logically progresses from initial state to goal.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Preserve logical order and completeness.\n"
            "- Use bullet points or numbered steps.\n"
            "- Do not include explanations, comments, or extra text."
        )
        response = self.llm.request([prompt]).strip()
        return response
