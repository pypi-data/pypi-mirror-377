# brainary/capabilities/reasoning/cot_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class CoTReasoning(Reasoning):
    NAME = "Chain-of-Thought Reasoning"
    DESC = (
        "Produces a sequential step-by-step reasoning chain. "
        "Best for arithmetic, logical, and multi-step tasks "
        "where transparency of intermediate steps is important. Outputs traces only."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using chain-of-thought reasoning. "
            "Generate a step-by-step reasoning chain without concluding. "
            "Do not output the final answer.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Step 1: ...\n"
            "- Step 2: ...\n"
            "- Step 3: ..."
        )
        return self.llm.request([prompt]).strip()
