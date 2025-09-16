from typing import List, Dict
from .critical_thinking_base import CriticalThinking


class BloomCriticalThinking(CriticalThinking):
    NAME = "Bloom’s Taxonomy"
    DESC = (
        "Uses Bloom’s higher-order cognitive skills to process the task. "
        "Performs analysis (break down into components), evaluation (judge quality and validity), "
        "and creation (propose new alternatives or syntheses). "
        "Best for instructional design, structured reasoning, or generating innovative solutions "
        "where deeper levels of cognition are required."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Apply Bloom’s higher-order taxonomy to the following task.\n\n"
            "## Task\n" + task + "\n\n"
            "## Process\n"
            "1. Analyze: break down into components.\n"
            "2. Evaluate: assess quality, validity, importance.\n"
            "3. Create: propose new synthesis, alternative solutions, or reformulations.\n\n"
            "Output under headings: Analyze, Evaluate, Create."
        )
        return self.llm.request([prompt]).strip()

