from pathlib import Path
from typing import List, Dict, Any
import statistics
import json

from brainary.llm.llm import LLM, AUX_MODEL


class Experience:
    """Single record of a capability-strategy performance history."""

    def __init__(self, capability: str, strategy: str, metadata: Dict[str, Any] = None):
        self.capability = capability
        self.strategy = strategy
        self.metadata = metadata or {}
        self.outcomes: List[float] = []
        self.usage_count: int = 0

    def record_outcome(self, score: float):
        self.outcomes.append(score)
        self.usage_count += 1

    @property
    def avg_outcome(self) -> float:
        return statistics.mean(self.outcomes) if self.outcomes else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "strategy": self.strategy,
            "avg_outcome": self.avg_outcome,
            "usage_count": self.usage_count,
            "metadata": self.metadata,
        }


class Knowledge:
    """Distilled abstract rules from raw experiences."""

    def __init__(self):
        self.rules: List[Dict] = []

    def add_rule(self, capability: str, condition: str, strategy: str, confidence: float):
        self.rules.append({
            "capability": capability,
            "condition": condition,  # textual condition (keywords, contexts)
            "strategy": strategy,
            "confidence": confidence,
        })

    def query(self, capability: str, context: str = "") -> List[Dict]:
        """Find matching rules given current context (simple keyword filter)."""
        matches = []
        for r in self.rules:
            if r["capability"] == capability and any(
                word in context.lower() for word in r["condition"].split()
            ):
                matches.append(r)
        return sorted(matches, key=lambda x: x["confidence"], reverse=True)


class ExperienceBase:
    """
    Episodic + semantic memory of capability-strategy use.
    - Stores raw experiences
    - Distills them into abstract knowledge rules
    """

    def __init__(self):
        self.memory: Dict[str, Dict[str, Experience]] = {}  # cap -> strat -> Experience
        self.knowledge = Knowledge()
        self.update_counter = 0

    def dump(self, path):
        import pickle
        with Path(path).open("wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path):
        import pickle
        with Path(path).open("rb") as f:
            return pickle.load(f)

    # -------- Raw Experience --------
    def inject(
        self,
        capability: str,
        strategy: str,
        outcome: float = 1.0,
        metadata: Dict[str, Any] = None,
    ):
        cap_mem = self.memory.setdefault(capability, {})
        exp = cap_mem.get(strategy)
        if exp is None:
            exp = Experience(capability, strategy, metadata)
            cap_mem[strategy] = exp
        exp.record_outcome(outcome)

    def record(
        self,
        capability: str,
        strategy: str,
        outcome: float,
        metadata: Dict[str, Any] = None,
    ):
        self.inject(capability, strategy, outcome, metadata)
        self.update_counter += 1
        if self.update_counter % 10 == 0:  # auto-distill every 10 updates
            self.distill()

    def query(self, capability: str) -> List[Experience]:
        """Return all experiences for a capability, sorted by performance."""
        if capability not in self.memory:
            return []
        return sorted(self.memory[capability].values(), key=lambda e: e.avg_outcome, reverse=True)

    def best_strategy(self, capability: str) -> str:
        """Return best-performing strategy for a capability (by average outcome)."""
        exps = self.query(capability)
        if not exps:
            return None
        return exps[0].strategy

    def all_strategies(self) -> Dict[str, List[str]]:
        return {cap: list(strats.keys()) for cap, strats in self.memory.items()}

    # -------- Distillation into Knowledge --------
    def distill(self):
        """
        Summarize experience records into abstract knowledge rules via LLM.
        Updates self.knowledge.
        """
        exp_dump = []
        for cap, strategies in self.memory.items():
            for strat, exp in strategies.items():
                exp_dump.append(
                    f"- {cap}:{strat}, avg_outcome={exp.avg_outcome:.2f}, used={exp.usage_count}"
                )
        exp_text = "\n".join(exp_dump) or "No experiences yet."

        prompt = (
            "You are a meta-cognition learner. Given past experiences with cognitive strategies, "
            "distill abstract rules about when certain strategies work best.\n\n"
            "## Experience Data\n"
            f"{exp_text}\n\n"
            "## Output Format\n"
            "Return a JSON list, each entry like:\n"
            "{ 'capability': 'reasoning', "
            "'condition': 'math, long instruction', "
            "'strategy': 'step_by_step', "
            "'confidence': 0.9 }"
        )

        response = LLM.get_by_name(AUX_MODEL).request([prompt])

        try:
            rules = json.loads(response)
            for r in rules:
                self.knowledge.add_rule(
                    capability=r["capability"],
                    condition=r["condition"],
                    strategy=r["strategy"],
                    confidence=r["confidence"],
                )
        except Exception:
            # fallback: ignore bad LLM output
            pass
