from brainary.core.ops.action_op import ActionOp

class Attention:
    def __init__(self):
        pass

    @staticmethod
    def apply_default(action: ActionOp):
        return "## Notice\n" + "\n".join(f"- please focus on **{attn}**." for attn in action.attentions)