# brainary/capabilities/registry.py
import logging

from typing import TypeVar, Generic, Type, Dict
T = TypeVar("T")

class CapabilityRegistry(Generic[T]):
    """Generic registry for any type of capability."""
    def __init__(self):
        self._registry: Dict[str, Type[T]] = {}

    def register(self, capability_cls: Type[T]):
        logging.info(f"{capability_cls.NAME} is registered into {T.__name__} registry.")
        if not isinstance(capability_cls, type):
            raise TypeError("Only classes can be registered.")
        if not hasattr(capability_cls, "NAME"):
            raise AttributeError("Capability class must have a NAME attribute.")
        self._registry[capability_cls.NAME] = capability_cls
        return capability_cls

    def list_all(self) -> str:
        lines = []
        for _, cls in self._registry.items():
            desc = getattr(cls, "DESC", "")
            lines.append(f"### {cls.NAME}\n{desc}\n")
        return "\n".join(lines)

    def validate(self, name: str) -> bool:
        return name in self._registry

    def get(self, name: str) -> Type[T]:
        return self._registry.get(name, None)

    def create(self, name: str, *args, **kwargs) -> T:
        cls = self.get(name)
        if cls is None:
            raise ValueError(f"Capability '{name}' not found in registry.")
        return cls(*args, **kwargs)



"""
This import is important to ensure the retristry can discover the capability strategies.
"""
import importlib
import pkgutil
import brainary.capabilities
def import_all_submodules(package):
    """
    Recursively import all submodules in a package.
    """
    if not hasattr(package, "__path__"):
        # Single file module, nothing to traverse
        return
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(name)
        if is_pkg:
            # Recursively traverse subpackage
            subpackage = importlib.import_module(name)
            import_all_submodules(subpackage)

import_all_submodules(brainary.capabilities)



"""
Define registries and register existing strategies.
"""
from brainary.capabilities.abstraction.abstraction_base import Abstraction
from brainary.capabilities.critical_thinking.critical_thinking_base import CriticalThinking
from brainary.capabilities.evaluation.evaluation_base import Evaluation
from brainary.capabilities.planning.planning_base import Planning
from brainary.capabilities.reasoning.reasoning_base import Reasoning
from brainary.capabilities.simulation.simulation_base import Simulation

ABSTRACTION_REGISTRY = CapabilityRegistry[Abstraction]()
for cls in Abstraction.__subclasses__():
    ABSTRACTION_REGISTRY.register(cls)
CRITICAL_THINKING_REGISTRY = CapabilityRegistry[CriticalThinking]()
for cls in CriticalThinking.__subclasses__():
    CRITICAL_THINKING_REGISTRY.register(cls)
EVALUATION_REGISTRY = CapabilityRegistry[Evaluation]()
for cls in Evaluation.__subclasses__():
    EVALUATION_REGISTRY.register(cls)
PLANNING_REGISTRY = CapabilityRegistry[Planning]()
for cls in Planning.__subclasses__():
    PLANNING_REGISTRY.register(cls)
REASONING_REGISTRY = CapabilityRegistry[Reasoning]()
for cls in Reasoning.__subclasses__():
    REASONING_REGISTRY.register(cls)
SIMULATION_REGISTRY = CapabilityRegistry[Simulation]()
for cls in Simulation.__subclasses__():
    SIMULATION_REGISTRY.register(cls)

CAPABILITIES: Dict[str, CapabilityRegistry] = {
    "abstraction": ABSTRACTION_REGISTRY,
    "critical_thinking": CRITICAL_THINKING_REGISTRY,
    "evaluation": EVALUATION_REGISTRY,
    "planning": PLANNING_REGISTRY,
    "reasoning": REASONING_REGISTRY,
    "simulation": SIMULATION_REGISTRY
}
