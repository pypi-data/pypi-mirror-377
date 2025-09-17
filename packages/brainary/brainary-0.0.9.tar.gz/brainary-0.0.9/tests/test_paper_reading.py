from typing import List
import brainary
from brainary.util.logging_util import init_logging

init_logging("log/tests/paper_reading.log")

brainary.install_vm("gpt-4o-mini", "")

Paper = brainary.define_type(
    type_name="Paper",
    text={"type": str, "desc": "paper content"},
)
p1 = Paper(text=open("tests/paper1.txt", "r").read().strip())
p2 = Paper(text=open("tests/paper2.txt", "r").read().strip())

summarize = brainary.define_action("Perform a literature review based on the given papers.", "paper_list", attentions=["insights", "combination"], output_constraints={"tone": "rigorous"})
summarize(paper_list=[p1, p2])