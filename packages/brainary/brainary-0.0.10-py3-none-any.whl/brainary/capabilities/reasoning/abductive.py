# brainary/capabilities/reasoning/abductive_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class AbductiveReasoning(Reasoning):
    NAME = "Abductive Reasoning"
    DESC = (
        "Generates plausible hypotheses to explain observations. "
        "Best for diagnostic, investigative, or exploratory tasks "
        "(e.g., medical reasoning, root-cause analysis). Produces explanatory traces."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using abductive reasoning. "
            "List possible explanations and assess their plausibility. "
            "Do not provide a final solution.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Hypothesis 1: ...\n"
            "- Hypothesis 2: ...\n"
            "- Evaluation: ...\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()
