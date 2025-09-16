from typing import List, Dict
from .critical_thinking_base import CriticalThinking


class RedTeamCriticalThinking(CriticalThinking):
    NAME = "Debiasing / Red Teaming"
    DESC = (
        "Acts as a red team to challenge reasoning, identify assumptions, and detect biases. "
        "Generates counterarguments and critiques to stress-test the robustness of an idea or solution. "
        "Most useful when addressing safety, reliability, fairness, or adversarial evaluation tasks."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Act as a critical red team. Challenge the following task or answer.\n\n"
            "## Task\n" + task+ "\n\n"
            "## Process\n"
            "1. Identify assumptions and potential biases.\n"
            "2. Challenge the reasoning with counterarguments.\n"
            "3. Suggest ways to improve robustness.\n\n"
            "Output under headings: Assumptions, Counterarguments, Improvements."
        )
        return self.llm.request([prompt]).strip()

