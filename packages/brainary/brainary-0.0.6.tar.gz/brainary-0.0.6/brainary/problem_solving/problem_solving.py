# Divergent Thinking
# Convergent Thinking
# Critical Thinking (Brainstorming, Validity Check, Critique, Aggregation)
# Triz-40 Principles 


from abc import ABCMeta, abstractmethod
from typing import Dict, List, Type

from brainary.llm.llm import LLM, AUX_MODEL


class ProblemSolving(metaclass=ABCMeta):
    NAME = ""
    DESC = ""

    def __init__(self, llm: LLM):
        self.llm = llm
    
    @abstractmethod
    def solve(self, messages: List[str]):
        raise NotImplementedError
    
class DefaultProblemSolving(ProblemSolving):
    NAME = "default"
    DESC = "Invoke LLMs directly without applying complex problem-solving strategies. This approach is best suited for simple, straightforward instructions or when no suitable strategy exists."
    
    def __init__(self, llm: LLM):
        super().__init__(llm)
    
    def solve(self, messages: List[str]):
        return self.llm.request(messages)
    

class ProblemSolvingRegistry:
    def __init__(self):
        self.strategies: Dict[str, ProblemSolving] = {"default": DefaultProblemSolving}

    def display(self):
        lines = []
        for _, strategy in self.strategies.items():
            lines.append(f"- {strategy.NAME}: {strategy.DESC}")
        return "\n".join(lines)

    def register(self, strategy: ProblemSolving):
        self.strategies[strategy.NAME] = strategy

    def validate(self, name: str):
        return name in self.strategies

    def get(self, name: str = "default") -> Type[ProblemSolving]:
        if name in self.strategies:
            return self.strategies[name]
        else:
            raise ValueError(f"Problem solving strategy '{name}' not found")