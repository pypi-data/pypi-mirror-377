# brainary/capabilities/reasoning/probabilistic_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class ProbabilisticReasoning(Reasoning):
    NAME = "Probabilistic Reasoning"
    DESC = (
        "Estimates likelihoods and uncertainties of different outcomes. "
        "Best for forecasting, risk analysis, and tasks involving incomplete or noisy data. "
        "Produces probability-based traces, not final answers."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using probabilistic reasoning. "
            "List possible outcomes, assign probabilities, and explain your estimates. "
            "Do not provide a final answer.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Outcome A: P=...\n"
            "- Outcome B: P=...\n"
            "- Outcome C: P=...\n"
            "- Notes: ...\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()
