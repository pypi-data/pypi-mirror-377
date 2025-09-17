# brainary/capabilities/reasoning/commonsense_reasoning.py
from brainary.capabilities.reasoning.reasoning_base import Reasoning

class CommonsenseReasoning(Reasoning):
    NAME = "Commonsense Reasoning"
    DESC = (
        "Applies everyday knowledge and heuristics. "
        "Best for ambiguous, under-specified, or human-centered tasks "
        "(e.g., daily life scenarios, intuitive judgments). Produces commonsense traces."
    )

    def reason(self, task: str) ->  str:
        prompt = (
            "Analyze the task using commonsense reasoning. "
            "Apply everyday knowledge, heuristics, and intuitive expectations. "
            "Do not solve the problem, only produce reasoning traces.\n\n"
            f"## Task\n{task}\n\n"
            "## Output Format\n"
            "- Assumption 1: ...\n"
            "- Assumption 2: ...\n"
            "- Heuristic: ...\n"
            "- Implication: ...\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()
