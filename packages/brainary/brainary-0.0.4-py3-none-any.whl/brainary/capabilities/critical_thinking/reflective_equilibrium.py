from typing import List, Dict
from .critical_thinking_base import CriticalThinking


class ReflectiveEquilibriumCriticalThinking(CriticalThinking):
    NAME = "Reflective Equilibrium / Dialectic"
    DESC = (
        "Uses reflective equilibrium (dialectical reasoning) to balance specific judgments "
        "with general principles through iterative adjustment. "
        "Considers counterexamples and alternative viewpoints, refining the task or argument until coherence is achieved. "
        "Particularly suited for tasks involving ethics, fairness, or conflicting principles."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Apply Reflective Equilibrium (dialectical reasoning) to the following task.\n\n"
            "## Task\n" + task+ "\n\n"
            "## Process\n"
            "1. State initial judgments or intuitions.\n"
            "2. Compare them with general principles.\n"
            "3. Introduce counterexamples or alternative views.\n"
            "4. Adjust until coherence is reached.\n\n"
            "Output under headings: Initial Judgments, Principles, Counterexamples, Adjustments, Equilibrium."
        )
        return self.llm.request([prompt]).strip()
