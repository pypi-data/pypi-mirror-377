# brainary/capabilities/critical_thinking_base.py
from abc import abstractmethod
from typing import List

from brainary.capabilities.base import Capability

class CriticalThinking(Capability):
    NAME = "Abstract Critical Thinking"
    DESC = (
        "Abstract base class for Critical Thinking capabilities. "
        "Should implement think(task: str) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def think(self, task: str) -> str:
        raise NotImplementedError

    def perform(self, task: str):
        return self.think(task)
