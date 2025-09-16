from typing import Any, Callable, List, Dict, Union, Optional, Mapping, Iterable

from brainary.core.ops.base_op import BaseOp


INDENT_UNIT = "  "

class CtxOp(BaseOp):

    def __init__(self, name: str, value: Union[str, dict]):
        self.name = name
        self.value = value

    def __repr__(self):
        def flatten_dict(d: dict, level=0):
            frags = []
            for k, v in d.items():
                if isinstance(v, str):
                    frags.append(INDENT_UNIT * level + f"- {k}: {v}")
                elif isinstance(v, dict):
                    frags.append(INDENT_UNIT * level + f"- {k}:\n{flatten_dict(v, level + 1)}")
            return "\n".join(frags)
        
        lines = [
            f"#### {self.name.replace('_',' ').title()}"
        ]
        if isinstance(self.value, str):
            lines.append(self.value)
        else:
            lines.append(flatten_dict(self.value))
        return '\n'.join(lines)
    
    def render(self, **kwargs):
        prompt = repr(self)
        return prompt