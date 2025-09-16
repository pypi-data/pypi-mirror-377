# brainary/vm.py
import json
from pathlib import Path
from typing import Any, Union
import logging
from brainary.core.runtime import Runtime
from brainary.core.scheduler import Scheduler
from brainary.core.monitor import Monitor
from brainary.core.experience import ExperienceBase
from brainary.core.ops import *
from brainary.llm.llm import LLM
from brainary.problem_solving.problem_solving import ProblemSolvingRegistry, ProblemSolving, DefaultProblemSolving
from brainary.capabilities.registry import CAPABILITIES

AUX_MODEL = "gpt-4o-mini"


"""
+---------------------------+
| Python Code / User Call   |
| e.g., action(), examine() |
+------------+--------------+
             |
             v
+---------------------------+
| BrainaryVM.execute_op()   |
+------------+--------------+
             |
             v
+---------------------------+
| Scheduler.estimate(op)    |
| - Use LLM & Experience    |
| - Select strategies       |
+------------+--------------+
             |
             v
+---------------------------+
| Scheduler.ensure_args()   |
| Scheduler.ensure_context()|
| - Fill missing args       |
| - Fill missing context    |
+------------+--------------+
             |
             v
+---------------------------+
| Problem Solver / LLM Exec |
| - Execute op with chosen  |
|   strategies & context    |
+------------+--------------+
             |
             v
+---------------------------+
| Monitor.do_monitor()       |
| - Evaluate performance    |
| - Track success/fail      |
+------------+--------------+
             |
             v
+---------------------------+
| ExperienceBase.update()    |
| - Record outcome          |
| - Update distilled        |
|   Knowledge               |
+------------+--------------+
             |
             v
+---------------------------+
| Scheduler.prioritize_strategies() |
| - Adjust strategy order  |
| - Prepare for next ops    |
+------------+--------------+
             |
             v
         Loop back

"""

class BrainaryVM:
    def __init__(self, model_name: str, experience_base_path: str=None):
        self.llm: LLM = LLM.get_by_name(model_name)
        self.runtime: Runtime = Runtime()
        self.experience_base_path = experience_base_path
        if self.experience_base_path and Path(self.experience_base_path).exists():
            self.experience_base: ExperienceBase = ExperienceBase.load(self.experience_base_path)
        else:
            self.experience_base: ExperienceBase =  ExperienceBase()
        self.problem_solving_registry = ProblemSolvingRegistry()
        # TODO: Add other capability registries

        self.scheduler: Scheduler = Scheduler(self.runtime, self.experience_base, self.problem_solving_registry)
        self.monitor: Monitor = Monitor(self.runtime)

    def __del__(self):
        if self.experience_base_path:
            self.experience_base.dump(self.experience_base_path)

    def accept_op(self, op: BaseOp, **kwargs):
        if isinstance(op, TypeOp):
            self.runtime.heap.add_obj(op)

        elif isinstance(op, CtxOp):
            self.runtime.heap.add_ctx(op)

        elif isinstance(op, (ActionOp, ExamineOp)):
            self.scheduler.enqueue(op, **kwargs)
            self._execute()

    # -------- Self-Regulation Loop per operation --------
    def _execute(self) -> Any:
        """
        Self-regulation loop per operation:
        1. Estimate capabilities and contexts
        2. Generate traces for critical thinking, planning, reasoning,
        evaluation, and simulation
        3. Execute operation via problem solver
        4. Monitor outcomes
        5. Update experience base
        6. Optional replanning
        """
        result = None

        while self.scheduler.has_next():
            # TODO: record the orignal op for replanning
            op, kwargs = self.scheduler.schedule_next()

            # --- Generate pre-analysis traces for capabilities ---
            pre_analysis = dict()
            for cap in ["critical_thinking", "reasoning", "abstraction", "simulation"]:
                strategy_name = getattr(op, cap, None)
                if strategy_name:
                    strategy_cls = CAPABILITIES[cap].get(strategy_name)
                    if strategy_cls:
                        capability_instance = strategy_cls(self.llm)
                        perform_method = getattr(capability_instance, "perform", None)
                        if perform_method:
                            trace_result = perform_method(op.render(**kwargs))
                            pre_analysis[f"{cap}_trace"] = trace_result

            logging.info(f"[VM] Execute {op}.\nArguments: {kwargs}")

            # --- Render final prompt with all traces ---
            messages = [op.render(**(kwargs | pre_analysis))]

            # --- Execute via Problem Solving ---
            if isinstance(op, ActionOp):
                solver: ProblemSolving = self.problem_solving_registry.get(op.problem_solving)(LLM.get_by_name(AUX_MODEL))
            else:
                solver: ProblemSolving = DefaultProblemSolving(LLM.get_by_name(AUX_MODEL))

            response = solver.solve(messages=messages)
            result = op.resolve(response)

            # --- Record Execution ---
            if isinstance(op, ActionOp):
                # Record in runtime
                self.runtime.record_execution(op, kwargs, pre_analysis, result, 0)

                evaluator_name = getattr(op, "evaluation", None)
                evaluation_method = None
                if evaluator_name:
                    evaluator_cls = CAPABILITIES["evaluation"].get(evaluator_name)
                    if evaluator_cls:
                        evaluator_instance = evaluator_cls(self.llm)
                        evaluation_method = getattr(evaluator_instance, "perform", None)
                
                # --- Collect trace scores for experience ---
                cap_evals = {}
                cap_scores = {}
                # TODO: evaluation for planning
                for cap in ["critical_thinking", "reasoning", "abstraction", "simulation"]:
                    if f"{cap}_trace" not in pre_analysis or not getattr(op, cap) or not evaluation_method:
                        continue
                    trace = {f"{cap}_trace": pre_analysis[f"{cap}_trace"]}
                    eval_output = evaluation_method(op.render(**(kwargs | trace)), result)
                    cap_evals[cap] = eval_output
                    outcome = self.monitor.estimate_trace_score(eval_output, cap)
                    cap_scores[cap] = outcome
                    strat = getattr(op, cap)
                    self.experience_base.record(cap, strat, outcome, 0)

                # --- Optional Resceduling if performance is low ---
                if evaluation_method:
                    eval_output = evaluation_method(op.render(**(kwargs | pre_analysis)), result)
                    if self.monitor.estimate_reward(eval_output) - op.expected_reward < 0.:
                        logging.info("[VM] Performance low. Triggering resceduling.")
                        feedback = []
                        # TODO: feedback for planning
                        for cap in ["critical_thinking", "reasoning", "abstraction", "simulation"]:
                            if f"{cap}_trace" not in pre_analysis or not getattr(op, cap) or cap not in cap_evals:
                                continue
                            strat = getattr(op, cap)
                            trace = pre_analysis[f"{cap}_trace"]
                            eval = cap_evals[cap]
                            feedback.append(f"### {cap.replace('_',' ').title()}\n#### Applied Strategy\n{strat}\n\n#### Trace\n{trace}\n\n#### Evaluation\n{eval}")
                        feedback.append(f"### Final Result\n#### {result}\n\n#### Evaluation\n{eval_output}")
                        self.scheduler.enqueue(op, "\n\n".join(feedback), **kwargs)

        return result



    



__VM__: BrainaryVM = None

def install_vm(model_name:str, experience_base:str=None):
    global __VM__
    if __VM__ is None:
        __VM__ = BrainaryVM(model_name, experience_base)