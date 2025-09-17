from typing import List, Dict
from .critical_thinking_base import CriticalThinking


class SocraticQuestioningCriticalThinking(CriticalThinking):
    NAME = "Socratic Questioning"
    DESC = (
        "Applies Socratic questioning to systematically probe reasoning. "
        "Explores clarity, assumptions, evidence, alternative viewpoints, and implications. "
        "Best for tasks requiring deep exploration, uncovering hidden assumptions, "
        "and strengthening arguments by disciplined inquiry."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Apply Socratic questioning to the following task.\n\n"
            "## Task\n" + task+ "\n\n"
            "## Process\n"
            "Use these categories:\n"
            "- Clarification Questions\n"
            "- Assumption Probes\n"
            "- Evidence Probes\n"
            "- Viewpoint Exploration\n"
            "- Implication Probes\n"
            "- Questioning the Question\n\n"
            "Output structured under these headings.\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()