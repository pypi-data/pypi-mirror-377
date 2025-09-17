# brainary/capabilities/reasoning/deductive_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class DeductiveReasoning(Reasoning):
    NAME = "Deductive Reasoning"
    DESC = (
        "Applies strict logical rules to derive conclusions from stated premises. "
        "Best for tasks with well-defined rules (e.g., logic puzzles, math proofs, "
        "formal argument analysis). Produces reasoning steps, not final answers."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using deductive reasoning. "
            "Show the premises, apply rules of logic, and outline intermediate conclusions. "
            "Do not provide the final answer.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Premise 1: ...\n"
            "- Premise 2: ...\n"
            "- Deduction Step 1: ...\n"
            "- Deduction Step 2: ..."
        )
        return self.llm.request([prompt]).strip()
