# completeness_check.py
from .evaluation_base import Evaluation

class CompletenessCheck(Evaluation):
    NAME = "Completeness Check"
    DESC = (
        "Ensure all required components, steps, or elements are present. "
        "Use this when output must satisfy a checklist or cover multiple criteria."
    )

    def evaluate(self, task: str, result: str):
        prompt = (
            "You are an evaluation agent. Check the output for completeness.\n\n"
            f"## Task\n{task}\n\n"
            f"## Output\n{result}\n\n"
            "## Guidelines\n"
            "- Verify that all expected components or steps are included.\n"
            "- Indicate 'complete' if all parts are present, otherwise 'incomplete' with brief note of missing elements."
        )
        return self.llm.request([prompt]).strip()
