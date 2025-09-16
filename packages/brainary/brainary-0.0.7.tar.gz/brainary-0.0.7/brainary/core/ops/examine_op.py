from typing import Any, Callable, List, Dict, Union, Optional

from brainary.capabilities.registry import CAPABILITIES
from brainary.core.ops import BaseOp, CtxOp

class ExamineOp(BaseOp):
    def __init__(
        self,
        condition: str,
        *params,
        contexts: Optional[List[CtxOp]] = None,
        attentions: Optional[List[Dict[str, Any]]] = None,
        thinking: Optional[str] = None,
    ):
        super(ExamineOp).__init__()
        self.params = params
        self.condition = condition
        self.contexts = contexts or []
        self.attentions = attentions or []
        self.thinking = thinking

        self.instruction = f"Judge: {self.condition}"

    def render(self, **kwargs) -> str:
        missing = [p for p in self.params if p not in kwargs]
        if missing:
            raise TypeError(f"Missing required parameter(s): {missing}")
        # extra = [k for k in kwargs if k not in self.params]
        # if extra:
        #     raise TypeError(f"Unexpected parameter(s): {extra}")

        # self._check_constraints(**kwargs)
        segments = []
        segments.append(f"Judge: {self.condition}\n\n")
        
        # --- Critical Thinking Analysis ---
        if getattr(self, "critical_thinking", None):
            if "pre_analysis" in kwargs and kwargs["pre_analysis"]:
                segments.append("## Critical Thinking Analysis\n")
                segments.append(kwargs.pop("pre_analysis") + "\n\n")

        # --- Inject Capabilities / Strategies ---
        cap_segments = []
        for cap in CAPABILITIES:
            strategy = getattr(self, cap, None)
            if strategy:
                cap_segments.append(f"- {cap.replace('_',' ').title()}: {strategy}")
        if cap_segments:
            segments.append("## Strategies / Capabilities\n" + "\n".join(cap_segments) + "\n\n")

        # --- Contexts ---
        if self.contexts:
            contexts = "\n\n".join(ctx.render() for ctx in self.contexts)
            segments.append(f"## Contexts\n{contexts}\n\n")

        # --- Arguments ---
        if kwargs:
            arg_segments = []
            for k, v in kwargs.items():
                arg_segments.append(f"### {k.replace('_',' ').title()}\n{v}")
            segments.append(f"## Arguments\n"+ "\n\n".join(arg_segments) + "\n\n")
            
        segments.append(f"## Output Constraints\nOnly output YES or NO without any comments or explanations.")
        return "".join(segments)
    
    def resolve(self, response) -> bool:
        return response.lower() == "yes"
        

    def __repr__(self):
        return f"Action(instruction={self.condition!r}, params={self.params})"