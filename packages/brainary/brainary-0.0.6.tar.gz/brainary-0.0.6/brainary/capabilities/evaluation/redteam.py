# red_team_evaluation.py
from .evaluation_base import Evaluation

class RedTeamEvaluation(Evaluation):
    NAME = "Red Team Evaluation"
    DESC = (
        "Actively challenge the output to identify flaws, errors, or hidden assumptions. "
        "Use this when outputs may contain vulnerabilities or require adversarial testing."
    )

    def evaluate(self, task: str, result: str):
        prompt = (
            "You are a red team evaluator. Critically examine the output for flaws, risks, and hidden assumptions.\n\n"
            f"## Task\n{task}\n\n"
            f"## Output\n{result}\n\n"
            "## Guidelines\n"
            "- Identify potential weaknesses, errors, or risky assumptions.\n"
            "- Suggest improvements or note risks succinctly.\n"
            "- Output as structured critique without extra commentary."
        )
        return self.llm.request([prompt]).strip()
