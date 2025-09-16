from typing import List, Dict
from brainary.capabilities.critical_thinking.critical_thinking_base import CriticalThinking


class PaulElderCriticalThinking(CriticalThinking):
    NAME = "Paul–Elder Framework"
    DESC = (
        "Applies the Paul–Elder critical thinking framework. "
        "Analyzes the task through the eight elements of thought "
        "(purpose, question, information, inference, concepts, assumptions, implications, point of view) "
        "and evaluates reasoning against intellectual standards "
        "(clarity, accuracy, precision, relevance, depth, breadth, logic, fairness). "
        "Best suited for tasks requiring systematic evaluation of reasoning quality."
    )

    def think(self, task: str) -> str:
        prompt = (
            "Apply Paul–Elder's critical thinking framework to the following task.\n\n"
            "## Task\n" + task + "\n\n"
            "## Process\n"
            "Analyze using the elements of thought: purpose, question, information, inference, "
            "concepts, assumptions, implications, point of view.\n\n"
            "Also evaluate using reasoning standards: clarity, accuracy, precision, relevance, "
            "depth, breadth, logic, fairness.\n\n"
            "Output your structured assessment clearly under these categories."
        )
        return self.llm.request([prompt]).strip()