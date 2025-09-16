# brainary/capabilities/planning_base.py
from abc import abstractmethod
from typing import List

from brainary.capabilities.base import Capability
from brainary.llm.llm import LLM

class Planning(Capability):
    NAME = "Abstract Planning"
    DESC = (
        "Abstract base class for Planning capabilities. "
        "Should implement plan(task: str) method."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    @abstractmethod
    def plan(self, task: str) -> str:
        raise NotImplementedError

    def replan(self, task: str, feedback: str) -> str:
        """
        Optional replanning based on feedback.
        By default, just calls plan again.
        """
        return self.plan(task)

    def perform(self, task: str, feedback: str = None):
        if feedback:
            return self.replan(task, feedback)
        else:
            return self.plan(task)