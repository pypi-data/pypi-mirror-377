from typing import List, Dict
from .critical_thinking_base import CriticalThinking


class RootCauseAnalysisCriticalThinking(CriticalThinking):
    NAME = "Root Cause Analysis (Five Whys)"
    DESC = (
        "Applies root cause analysis to identify underlying causes of a problem. "
        "Uses the 'Five Whys' method to iteratively ask why until the fundamental cause is exposed. "
        "Best for debugging reasoning failures, diagnosing issues, and problem-solving in complex tasks."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Apply Root Cause Analysis (Five Whys) to the following task.\n\n"
            "## Task\n" + task+ "\n\n"
            "## Process\n"
            "Ask 'Why?' iteratively up to five times to identify the root cause.\n"
            "Output under the following format:\n"
            "- Why 1:\n- Why 2:\n- Why 3:\n- Why 4:\n- Why 5:\n- Root Cause:"
        )
        return self.llm.request([prompt]).strip()