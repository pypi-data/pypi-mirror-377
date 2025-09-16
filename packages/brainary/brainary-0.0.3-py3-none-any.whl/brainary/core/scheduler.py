import time
import heapq
import json
from typing import Union, Dict

from brainary.core.runtime import Runtime
from brainary.llm.llm import LLM, AUX_MODEL
from brainary.core.ops import *
from brainary.core.experience import ExperienceBase
from brainary.problem_solving.problem_solving import ProblemSolvingRegistry
from brainary.capabilities.registry import CAPABILITIES


class Scheduler:
    def __init__(self, runtime: Runtime, experience: ExperienceBase, problem_solving_registry: ProblemSolvingRegistry):
        self.runtime = runtime
        self.experience = experience
        self.problem_solving_registry = problem_solving_registry
        self.ready_queue = []


    def enqueue(self, op: Union[ActionOp, ExamineOp], feedback: str=None, **kwargs):
        op, kwargs = self._estimate(op, feedback=feedback, **kwargs)
        timestamp = time.time()
        heapq.heappush(self.ready_queue, (timestamp, op, kwargs))

    def has_next(self):
        return len(self.ready_queue) > 0

    def schedule_next(self):
        if not self.ready_queue:
            return None, None
        _, op, kwargs = heapq.heappop(self.ready_queue)
        return op, kwargs
    

    # -------- Estimation --------
    def _estimate(self, op: Union[ActionOp, ExamineOp], feedback: str = None, **kwargs):
        """
        Estimate required capabilities, contexts, and strategies.
        If feedback is provided, perform dynamic replanning.
        """

        # # Step: adjust the instruction if necessary
        # adjusted_instruction = self._adjust_instruction(op, feedback=feedback)
        # op.instruction = adjusted_instruction

        if isinstance(op, ActionOp):
            # Step: Problem Solving Strategy
            self._infer_problem_solving_strategy(op)

            # Step: Infer or Re-evaluate capabilities dynamically
            self._infer_capabilities(op, feedback=feedback)

        planner_name = getattr(op, "planning", None)
        if planner_name:
            planner_cls = CAPABILITIES["planning"].get(planner_name)
            if planner_cls:
                planner_instance = planner_cls(self.llm)
                perform_method = getattr(planner_instance, "perform", None)
                planning_result = perform_method(op.render(**kwargs), feedback)
                op.instruction = planning_result

        # Step: Infer arguments and context
        kwargs = self._infer_args(op, **kwargs)
        self._infer_context(op)

        if isinstance(op, ExamineOp):
            return op, kwargs

        # Step: Compute expected reward
        self._expected_reward(op)

        return op, kwargs

    # -------- Instruction Adjustment --------
    def _adjust_instruction(self, op: Union[ActionOp, ExamineOp], feedback: str=None) -> str:
        # TODO: estimate whether to call planning/replanning at meta-cognition level. This may break down an action into a pok program.
        if not feedback:
            prompt = (
                "Analyze the following instruction. Estimate its complexity, and only if the instruction is extremely complex, decompose it into smaller sub-instructions. Otherwise, do not perform any breakdown.\n\n"
                f"## Instruction\n{op.instruction}\n\n"
                "## Output Constraints\n"
                "- If no breakdown is needed, return an empty text.\n"
                "- Otherwise, output the sub-instructions as a list in the following format:\n"
                "  - Instruction 1\n"
                "  - Instruction 2\n"
                "  - ...\n"
                "- Do not include explanations, comments, or extra content."
            )
            response = LLM.get_by_name(AUX_MODEL).request([prompt]).strip()
        else:
            prompt = (
                "Reanalyze the following instruction in light of the feedback. Analyze the following instruction. Estimate its complexity, and only if the instruction is extremely complex and the feedback is negative, decompose it into smaller sub-instructions. Otherwise, do not perform any breakdown..\n\n"
                f"## Instruction\n{op.instruction}\n\n"
                f"## Feedback\n{feedback}\n\n"
                "## Output Constraints\n"
                "- If no breakdown is needed, return an empty text.\n"
                "- Otherwise, output the sub-instructions as a list in the following format:\n"
                "  - Instruction 1\n"
                "  - Instruction 2\n"
                "  - ...\n"
                "- Do not include explanations, comments, or extra content."
            )
            response = LLM.get_by_name(AUX_MODEL).request([prompt]).strip()
        return f"{op.instruction}\n{response}".strip()

    # -------- Capability/Strategy Inference --------
    def _infer_problem_solving_strategy(self, op: ActionOp) -> list:
        if self.problem_solving_registry.validate(op.problem_solving):
            return
        prompt = (
            "Given the instruction, decide which problem solving strategy is needed.\n\n"
            f"## Instruction\n{op.instruction}\n\n"
            "## Available Strategies\n"
            f"{self.problem_solving_registry.display()}\n\n"
            "## Output Constraints\n"
            "- Output the name of the needed strategy. Ensure the full strategy name is preserved exactly as it appears, including the portion between '-' and ':'.\n"
            "- Do not include explanations, comments, or extra content."
        )
        response = LLM.get_by_name(AUX_MODEL).request([prompt]).strip()
        if self.problem_solving_registry.validate(response):
            op.problem_solving = response
        

    def _infer_capabilities(self, op: ActionOp, feedback: str = None) -> None:
        """
        Decide which capabilities and strategies are needed.
        If feedback is provided (replanning), the LLM may reconsider strategy selection.
        """

        # Step 0: Prompt LLM to select relevant capabilities
        prompt = (
            "Given the instruction"
            + (", and feedback from previous execution" if feedback else "")
            + ", decide which cognitive capabilities are required.\n\n"
            f"## Instruction\n{op.instruction}\n\n"
        )
        if feedback:
            prompt += f"## Feedback\n{feedback}\n\n"

        prompt += "## Available Capabilities\n" + "\n".join(f"- {cap}" for cap in CAPABILITIES) + "\n\n"
        prompt += (
            "Output JSON:\n"
            "{ 'capabilities': [capability1, capability2, ...] }\n"
            "Only output valid JSON, no explanations."
        )

        response = LLM.get_by_name(AUX_MODEL).request([prompt])
        try:
            selected_caps = json.loads(response).get("capabilities", [])
        except Exception:
            selected_caps = []

        cap_strategies = {}
        for cap in selected_caps:
            if not hasattr(op, cap):
                continue

            # Step 1: Consult distilled knowledge
            rules = self.experience.knowledge.query(cap, op.instruction)
            if rules:
                cap_strategies[cap] = rules[0]["strategy"]
                continue

            # Step 2: Consult episodic experience
            best = self.experience.best_strategy(cap)
            if best:
                cap_strategies[cap] = best
                continue

            # Step 3: LLM-based strategy selection
            prompt = (
                f"Given the instruction"
                + (f" and feedback: {feedback}" if feedback else "")
                + f", decide the most suitable strategy for {cap.replace('_',' ')}.\n\n"
                f"## Instruction\n{op.instruction}\n\n"
                "## Available Strategies\n"
                f"{CAPABILITIES[cap].list_all()}\n\n"
                "## Output Constraints\n"
                "- Output only the exact strategy name.\n"
                "- Do not output explanations or comments."
            )
            response = LLM.get_by_name(AUX_MODEL).request([prompt]).strip()
            cap_strategies[cap] = response

        # Assign strategies to the operation dynamically
        for cap, strat in cap_strategies.items():
            setattr(op, cap, strat)


    def _expected_reward(self, op: Union[ActionOp]) -> float:
        """
        Compute expected reward of an operation using:
        1. Knowledge-based confidence
        2. Episodic average outcome
        3. Trace scores of the capabilities
        """
        if op.expected_reward is not None:
            return

        strategies = {
            cap: getattr(op, cap) for cap in CAPABILITIES if getattr(op, cap)
        }

        reward_sum = 0.0
        weight_count = 0

        for cap, strat in strategies.items():
            # Step 1: Knowledge-based confidence
            rules = self.experience.knowledge.query(cap, op.instruction)
            if rules:
                reward_sum += rules[0]["confidence"]
                weight_count += 1

            # Step 2: Episodic average outcome
            exp = self.experience.memory.get(cap, {}).get(strat)
            if exp:
                reward_sum += exp.avg_outcome
                weight_count += 1

                # Step 3: Trace scores contribution
                trace_scores = exp.avg_trace_scores()
                if cap in trace_scores:
                    reward_sum += trace_scores[cap]
                    weight_count += 1

        op.expected_reward = reward_sum / max(1, weight_count)


    
    # -------- Context/Args Completion --------
    def _infer_args(self, op: Union[ActionOp, ExamineOp], **kwargs):
        if len(self.runtime.heap.objs) == 0:
            return kwargs
        existing_params = "\n".join(f"- {param}" for param in op.params)
        missing_params = LLM.get_by_name(AUX_MODEL).request([(
            "Infer the missing parameter names for the given instruction. The inferred names must exactly match entries (class names) from the list of valid data types.\n\n"
            f"## Instruction: {op.instruction}\n\n"
            f"## Existing Parameter Names\n{existing_params}\n\n"
            f"## Valid Data Types\n{self.runtime.heap.display_types()}\n\n"
            "## Output Constraints\n"
            "- Output as list in the following format:\n"
            "   - Name 1\n"
            "   - Name 2\n"
            "   - ...\n"
            "- Do not include explanations, comments, or extra content."
        )])
        params = list(op.params)
        for param in missing_params.split("\n"):
            if param.strip():
                params.append(param.strip("- ").replace(" ", "_").lower())
        op.params = tuple(params)
        missings = [p for p in op.params if p not in kwargs]
        for param in missings:
            obj = self.runtime.heap.resolve_obj(param)
            kwargs[param] = obj if obj is not None else "Not specified"
        return kwargs

    def _infer_context(self, op: Union[ActionOp, ExamineOp]):
        if len(self.runtime.heap.ctxs) == 0:
            return
        existing_ctxs = "\n".join(f"- {ctx.name}" for ctx in op.contexts)
        missing_ctxs = LLM.get_by_name(AUX_MODEL).request([(
            "Infer the missing context fields for the given instruction. The inferred names must exactly match entries from the list of valid context fields.\n\n"
            f"## Instruction\n{op.instruction}\n\n"
            f"## Existing Context Fields\n{existing_ctxs}\n\n"
            f"## Valid Context Fields\n{self.runtime.heap.display_ctxs()}\n\n"
            "## Output Constraints\n"
            "- Output as list in the following format:\n"
            "   - Field 1\n"
            "   - Field 2\n"
            "   - ...\n"
            "- Do not include explanations, comments, or extra content."

        )])
        contexts = list(op.contexts)
        for ctx in missing_ctxs.split("\n"):
            ctx = self.runtime.heap.resolve_ctx(ctx)
            if ctx:
                contexts.append(ctx)
        op.contexts = tuple(contexts)
