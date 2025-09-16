from abc import ABC, abstractmethod
import json


class BaseOp(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def render(self, **kwargs) -> str:
        raise NotImplementedError
    
    def resolve(self, response:str):
        return response