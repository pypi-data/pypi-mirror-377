# brainary/capabilities/reasoning/inductive_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class InductiveReasoning(Reasoning):
    NAME = "Inductive Reasoning"
    DESC = (
        "Generalizes from specific observations to broader patterns. "
        "Best for tasks involving pattern recognition, data analysis, trend prediction, "
        "or incomplete evidence. Produces traces of observations and generalizations."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using inductive reasoning. "
            "List specific observations, extract patterns, and propose generalizations. "
            "Do not give the final answer.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Observation 1: ...\n"
            "- Observation 2: ...\n"
            "- Pattern: ...\n"
            "- Generalization: ...\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()
