from brainary.capabilities.planning.planning_base import Planning
from brainary.llm.llm import LLM

class DirectPlanning(Planning):
    NAME = "Direct Planning (Direct LLM Invocation)"
    DESC = (
        "Fallback strategy that directly asks the LLM to produce a plan. "
        "Suitable for simple or moderately complex instructions where no specialized decomposition is needed."
    )

    def plan(self, task: str) -> str:
        prompt = (
            "Given the task, decide whether a breakdown into sub-instructions is necessary. "
            "If unnecessary, return an empty text; otherwise, output a list of sub-instructions.\n\n"
            f"## Task\n{task}\n\n"
            "## Output constraints\n- List format if breakdown is needed.\n- No explanations."
        )
        return self.llm.request([prompt]).strip()

    def replan(self, task: str, feedback: str) -> str:
        prompt = (
            "Reanalyze the task based on feedback.\n\n"
            f"## Task\n{task}\n\n## Feedback\n{feedback}\n\n"
            "## Output constraints\n- Return list of sub-instructions if necessary.\n- No extra text."
        )
        return self.llm.request([prompt]).strip()
