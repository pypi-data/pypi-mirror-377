# brainary/capabilities/evaluation_base.py
from abc import abstractmethod
from typing import List

from brainary.capabilities.base import Capability

class Evaluation(Capability):
    NAME = "Abstract Evaluation"
    DESC = (
        "Abstract base class for Evaluation capabilities. "
        "Should implement evaluate(task: str) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def evaluate(self, task: str, result: str):
        raise NotImplementedError

    def perform(self, task: str, result: str):
        return self.evaluate(task, result)
