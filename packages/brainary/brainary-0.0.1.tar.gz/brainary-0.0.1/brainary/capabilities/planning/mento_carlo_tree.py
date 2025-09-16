# brainary/capabilities/planning/mcts_planning.py
from typing import List
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class MCTSPlanning(Planning):
    NAME = "Monte Carlo Tree Search Planning"
    DESC = (
        "Uses Monte Carlo Tree Search (MCTS) to explore possible sequences of actions "
        "and select the path with the highest expected reward. Suitable for complex decision "
        "spaces, games, or tasks where evaluating multiple action sequences is necessary."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, task: str) -> str:
        """
        Generates a plan by performing Monte Carlo simulations of possible action sequences
        and selecting the sequence with the best expected outcome.
        """
        prompt = (
            "You are an expert planner using Monte Carlo Tree Search (MCTS).\n\n"
            "Given the task, perform the following:\n"
            "- Identify possible sequences of actions.\n"
            "- Simulate outcomes for each sequence.\n"
            "- Evaluate the expected reward for each sequence.\n"
            "- Select the sequence with the highest expected reward.\n"
            "- Output the plan in clear steps.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Constraints\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        response = self.llm.request([prompt]).strip()
        return response

    def replan(self, task: str, feedback: str) -> str:
        """
        Adjusts the MCTS plan based on feedback or new constraints.
        """
        prompt = (
            "You are an expert planner using Monte Carlo Tree Search (MCTS).\n\n"
            "Adjust the previous plan based on feedback or updated constraints.\n"
            "- Re-evaluate possible action sequences.\n"
            "- Re-simulate outcomes.\n"
            "- Choose the sequence with the highest expected reward.\n\n"
            f"## Task\n{task}\n\n"
            f"## Feedback / Changes\n{feedback}\n\n"
            "## Output Constraints\n"
            "- Preserve the structured sequence of actions.\n"
            "- Use bullet points or numbered steps.\n"
            "- Do not include explanations, comments, or extra content."
        )
        response = self.llm.request([prompt]).strip()
        return response
