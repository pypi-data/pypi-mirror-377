import json
from typing import Any, Callable, List, Dict, Union, Optional

from brainary.core.ops import BaseOp, CtxOp
from brainary.capabilities.registry import CAPABILITIES
from brainary.llm.llm import AUX_MODEL, LLM

MAX_ENERGY = 100000


class ActionOp(BaseOp):
    def __init__(
        self,
        instruction: str,
        *params,
        contexts: Optional[List[CtxOp]] = None,
        input_constraints: Optional[Dict[str, Any]] = None,
        output_constraints: Optional[Dict[str, Any]] = None,
        callbacks: Optional[List[Callable[[Any], Any]]] = None,
        attentions: Optional[List[Dict[str, Any]]] = None,
        energy: Optional[int] = None,

        problme_solving: Optional[str] = None,
        critical_thinking: Optional[str] = None,
        
        # capabilities
        planning: Optional[str] = None,
        reasoning: Optional[str] = None,
        evaluation: Optional[str] = None,
        memory_recall: Optional[str] = None,
        simulation: Optional[str] = None,
        abstraction: Optional[str] = None,

        expected_reward: Optional[float] = 0.5,

        return_in_json: bool = False
    ):
        super(ActionOp).__init__()
        self.instruction = instruction
        self.params = params
        self.contexts = contexts or []
        self.input_constraints = input_constraints or dict()
        self.output_constraints = output_constraints or dict()
        self.callbacks = callbacks or []
        self.attentions = attentions or []
        self.energy = energy or MAX_ENERGY
        self.problem_solving = problme_solving
        self.critical_thinking = critical_thinking
        self.planning = planning
        self.reasoning = reasoning
        self.evaluation = evaluation
        self.memory_recall = memory_recall
        self.simulation = simulation
        self.abstraction = abstraction
        self.expected_reward = expected_reward
        self.return_in_json = return_in_json
        

    def _check_input_constraints(self, **kwargs):
        for name, value in self.input_constraints.items():
            # TODO: validate constraint
            pass

    def render(self, **kwargs) -> str:
        """
        Render the instruction with contexts, arguments, output constraints,
        and capability traces (critical thinking, planning, reasoning,
        evaluation, simulation), including strategy names.
        """
        segments = []

        # --- Instruction ---
        segments.append(f"### Instruction\n{self.instruction}\n\n")

        # --- Contexts ---
        if getattr(self, "contexts", None) and self.contexts:
            contexts = "\n\n".join(ctx.render() for ctx in self.contexts)
            segments.append(f"### Contexts\n{contexts}\n\n")

        # --- Pre-analysis traces with strategy names ---
        for cap in ["critical_thinking", "planning", "reasoning", "evaluation", "simulation"]:
            strategy_name = getattr(self, cap, None)
            trace_name = f"{cap}_trace"
            trace = kwargs.pop(trace_name, None)

            if trace:
                display_name = cap.replace("_", " ").title() + " Trace"
                segments.append(f"### {display_name} (Strategy: {strategy_name})\n")
                if isinstance(trace, dict):
                    import json
                    trace_str = json.dumps(trace, indent=2)
                else:
                    trace_str = str(trace)
                segments.append(f"{trace_str}\n\n")

        # --- Arguments ---
        if kwargs:
            arguments = []
            for k, v in kwargs.items():
                k_fmt = " ".join(w[0].upper() + w[1:] for w in k.split("_"))
                arguments.append(f"#### {k_fmt}\n{v}")
            arguments = "\n\n".join(arguments)
            segments.append(f"### Arguments\n{arguments}\n\n")

        # --- Output Constraints ---
        if getattr(self, "output_constraints", None) and self.output_constraints:
            constraints = "\n".join(f"- {k}: {v}" for k, v in self.output_constraints.items())
            segments.append(f"### Output Constraints\n{constraints}")

        return "".join(segments)



        
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"Action({fields})"
    
    def resolve(self, response):
        if self.return_in_json:
            return json.loads(response.strip())
        return response