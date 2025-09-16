# brainary/capabilities/reasoning/counterfactual_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class CounterfactualReasoning(Reasoning):
    NAME = "Counterfactual Reasoning"
    DESC = (
        "Explores 'what if' scenarios by altering assumptions. "
        "Best for risk assessment, causal inference, and decision-making under uncertainty. "
        "Outputs counterfactual traces."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using counterfactual reasoning. "
            "Propose 'what if' scenarios, vary assumptions, and explain possible outcomes. "
            "Do not solve the problem.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Counterfactual 1: If ..., then ...\n"
            "- Counterfactual 2: If ..., then ...\n"
            "- Implications: ..."
        )
        return self.llm.request([prompt]).strip()
