from collections import defaultdict
from typing import Any, OrderedDict

from brainary.core.ops import TypeOp, CtxOp


"""
Maybe we can refer to the JVM memory model. For example, we can allocte a seperate area for storing instructions, enabling better instruction scheduling.
┌────────────────────────────┐
│       JVM Memory Model     │
├─────────────┬──────────────┤
│  Heap       │  Stores object instances, arrays, Class objects      │
├─────────────┼──────────────┤
│  Method Area│  Stores class-level metadata, including:             │
│             │  ├─ Class name, superclasses, interfaces             │
│             │  ├─ Constant pool (literals, symbols)                │
│             │  ├─ Method info (including bytecode instructions)    │
│             │  └─ Field info, annotations, access flags, etc.      │
│             │                                                      │
│             │  🔸 Bytecode is stored here!                         │
├─────────────┼──────────────┤
│  Stack      │  Per-thread call stacks (frames for each method call)│
├─────────────┼──────────────┤
│ Native Stack│  Supports native (JNI) method calls                  │
├─────────────┼──────────────┤
│ PC Register │  Program Counter: points to current bytecode instruction │
└─────────────┴──────────────┘
"""

class Memory:
    def __init__(self, max_capacity=100, embedding_model=None):
        self.types = set()
        self.objs = list()
        self.ctxs = list()
        self.obj_index = defaultdict(list)
        self.ctx_index = defaultdict(CtxOp)
        self.embedding_model = embedding_model
        
    def add_obj(self, obj:TypeOp):
        self.types.add(obj.__class__)
        self.objs.append(obj)
        self.obj_index[obj.__class__.__name__.split(".")[-1].lower()].append(obj)

    def add_ctx(self, ctx:CtxOp):
        self.ctxs.append(ctx)
        self.ctx_index[ctx.name.lower()] = ctx

    def display_types(self):
        return "\n\n".join("- " + t.type_repr() for t in self.types)
    
    def display_ctxs(self):
        return "\n\n".join(repr(c) for c in self.ctxs)

    def resolve_obj(self, ref: str, top_k=1) -> str:
        # 1. Try exact match
        obj = self.obj_index.get(ref.lower().replace(" ", "_"), [None])[-1]
        if obj is not None:
            return obj

        # 2. Semantic search
        if self.embedding_model:
            return self._semantic_search(ref, self.objs, top_k=top_k)

        return None
    
    def resolve_ctx(self, ref: str, top_k=1) -> str:
        # 1. Try exact match
        ctx = self.ctx_index.get(ref.lower().replace(" ", "_"), None)
        if ctx is not None:
            return ctx

        # 2. Semantic search
        if self.embedding_model:
            return self._semantic_search(ref, self.ctxs, top_k=top_k)
        return None

    def _semantic_search(self, query: str, all_entries: list, top_k=1):
        """Search STM + LTM for best semantic match to query."""
        
        return all_entries[-1]

        # Embed query
        query_emb = self.embedding_model.embed(query)

        # Score by similarity
        scored = []
        for key, value in all_entries:
            score = self.embedding_model.similarity(query_emb, key)
            scored.append((score, value))

        scored.sort(reverse=True)
        return scored[0][1] if scored else None