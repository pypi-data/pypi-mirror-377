# accuracy_check.py
from .evaluation_base import Evaluation

class AccuracyCheck(Evaluation):
    NAME = "Accuracy Check"
    DESC = (
        "Compare outputs against reference or gold standard for correctness. "
        "Use this when verification against known answers, benchmarks, or expected values is required."
    )

    def evaluate(self, task: str, result: str):
        prompt = (
            "You are an evaluation agent. Assess the accuracy of the output below.\n\n"
            f"## Task\n{task}\n\n"
            f"## Output\n{result}\n\n"
            "## Guidelines\n"
            "- Evaluate correctness against known facts, expected results, or gold standards.\n"
            "- Provide a numeric score (0.0-1.0) and a brief rationale.\n"
            "- Keep the explanation concise and structured."
        )
        return self.llm.request([prompt]).strip()
