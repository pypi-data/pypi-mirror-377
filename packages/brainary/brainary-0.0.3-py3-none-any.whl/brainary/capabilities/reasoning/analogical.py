# brainary/capabilities/reasoning/analogical_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class AnalogicalReasoning(Reasoning):
    NAME = "Analogical Reasoning"
    DESC = (
        "Uses analogies between familiar and unfamiliar domains to explain or reason. "
        "Best for creative problem-solving, teaching, or understanding abstract concepts "
        "through concrete comparisons. Produces analogy traces."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using analogical reasoning. "
            "Identify a familiar analogy and explain how it maps to the problem. "
            "Do not provide a final solution.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Analogy Source: ...\n"
            "- Analogy Target: ...\n"
            "- Mapping: ...\n"
            "- Insights: ..."
        )
        return self.llm.request([prompt]).strip()
