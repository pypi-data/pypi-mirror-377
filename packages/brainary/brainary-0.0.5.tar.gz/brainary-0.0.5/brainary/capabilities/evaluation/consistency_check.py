# consistency_check.py
from .evaluation_base import Evaluation

class ConsistencyCheck(Evaluation):
    NAME = "Consistency Check"
    DESC = (
        "Verify that outputs are logically consistent with constraints, prior facts, or rules. "
        "Use this when correctness depends on logical coherence or adherence to structured rules, e.g., calculations, schedules, sequences."
    )

    def evaluate(self, task: str, result: str):
        prompt = (
            "You are an evaluation agent. Analyze the following task/output for logical consistency.\n\n"
            f"## Task\n{task}\n\n"
            f"## Output\n{result}\n\n"
            "## Guidelines\n"
            "- Check for contradictions or violations of constraints.\n"
            "- Highlight inconsistencies with concise reasoning.\n"
            "- Output only 'consistent' or 'inconsistent' with a brief rationale."
        )
        return self.llm.request([prompt]).strip()
