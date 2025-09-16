from typing import List, Dict
from .critical_thinking_base import CriticalThinking


class SixThinkingHatsCriticalThinking(CriticalThinking):
    NAME = "Six Thinking Hats"
    DESC = (
        "Uses Edward de Bono’s Six Thinking Hats method to examine a problem from multiple perspectives. "
        "White Hat (facts), Red Hat (feelings), Black Hat (risks), Yellow Hat (benefits), "
        "Green Hat (creativity), Blue Hat (process). "
        "Best for balanced, multi-perspective evaluation and creative idea generation."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Apply Edward de Bono’s Six Thinking Hats to the following task.\n\n"
            "## Task\n" + task+ "\n\n"
            "## Process\n"
            "Output under these headings:\n"
            "- White Hat (facts & data)\n"
            "- Red Hat (feelings & intuition)\n"
            "- Black Hat (risks & problems)\n"
            "- Yellow Hat (benefits & positives)\n"
            "- Green Hat (creativity & alternatives)\n"
            "- Blue Hat (process & control)"
        )
        return self.llm.request([prompt]).strip()