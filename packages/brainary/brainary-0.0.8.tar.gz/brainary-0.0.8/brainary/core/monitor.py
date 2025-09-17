# brainary/core/monitor.py
from typing import Any, Callable, Dict
from brainary.core.ops.action_op import ActionOp
from brainary.core.runtime import Runtime
from brainary.llm.llm import LLM, AUX_MODEL
import json
import statistics

class Monitor:
    """
    Tracks system performance, capability trace quality, and execution outcomes.
    Provides feedback metrics for the scheduler and experience updates.
    """

    def __init__(self, runtime: Runtime):
        self.runtime = runtime

    # -------- System Performance --------
    def estimate_reward(self, eval_output: str) -> float:
        """
        Returns a performance metric (0..1) based on the last execution,
        taking into account capability traces (reasoning, critical thinking, evaluation, simulation).
        """
        if not self.runtime.execution:
            return 1.0

        # Get last execution
        op, kwargs, pre_analysis, result, cost = self.runtime.execution[-1]
        op: ActionOp

        # --- Basic execution quality ---
        prompt = (
            "Given the instruction and execution result, output a performance score between 0..1.\n\n"
            f"## Instruction\n{op.instruction}\n\n"
            f"## Execution Result\n{result}\n\n"
            f"## Evaluation\n{eval_output}\n\n"
            "## Output Constraints\n"
            "- Float in range 0..1\n"
            "- No extra comments or text"
        )
        try:
            score = float(LLM.get_by_name(AUX_MODEL).request([prompt]).strip())
        except Exception:
            score = 0.5  # fallback

        return max(0.0, min(1.0, score))
    

    def estimate_trace_score(self, eval_output: str, capability: str) -> float:
        """
        Estimate a score (0..1) for a specific capability trace.
        """
        if not self.runtime.execution:
            return 1.0
        
        # Get last execution
        op, kwargs, pre_analysis, result, cost = self.runtime.execution[-1]
        op: ActionOp

        if f"{capability}_trace" not in pre_analysis:
            return 0
        
        trace = pre_analysis[f"{capability}_trace"]

        prompt = (
            f"Assess the quality and usefulness of the {capability.replace('_', ' ')} trace for the instruction.\n\n"
            f"## Instruction\n{op.instruction}\n\n"
            f"## Trace\n{trace}\n\n"
            f"## Execution Result\n{result}\n\n"
            f"## Evaluation\n{eval_output}\n\n"
            "## Output Constraints\n"
            "- Float between 0..1\n"
            "- No extra text"
        )
        try:
            score = float(LLM.get_by_name(AUX_MODEL).request([prompt]).strip())
        except Exception:
            score = 0.5  # fallback
        return max(0.0, min(1.0, score))


    # -------- Stats Summary --------
    def collect_stats(self) -> Dict[str, float]:
        """
        Returns summary stats for monitoring and potential replanning.
        """
        reward = self.estimate_reward()
        return {
            "reward": reward,
            "executions": len(self.runtime.execution)
        }
