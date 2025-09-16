# brainary/capabilities/reasoning_base.py
from abc import abstractmethod
from typing import List

from brainary.capabilities.base import Capability

class Reasoning(Capability):
    NAME = "Abstract Reasoning"
    DESC = (
        "Abstract base class for Reasoning capabilities. "
        "Should implement reason(task: str) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def reason(self, task: str):
        raise NotImplementedError

    def perform(self, task: str):
        return self.reason(task)
