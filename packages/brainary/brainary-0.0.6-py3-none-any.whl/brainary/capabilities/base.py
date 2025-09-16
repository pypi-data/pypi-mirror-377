# brainary/capabilities/base.py
from abc import ABCMeta, abstractmethod
from typing import List

class Capability(metaclass=ABCMeta):
    NAME = "Generic Capability"
    DESC = "Abstract base class for all capabilities. Should be extended by concrete implementations."

    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def perform(self,task: str) -> str:
        """Execute the capability on a given task."""
        raise NotImplementedError
