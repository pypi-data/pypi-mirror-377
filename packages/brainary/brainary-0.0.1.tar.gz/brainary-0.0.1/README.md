# Brainary + PoK
A brain-inspired computing architecture (Brainary) and a language for knowledge programming (PoK).


## Workflow
┌───────────────────────────┐
│       Python Script       │
│  (calls Brainary APIs)    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Brainary VM          │
│  accept_op(ActionOp)      │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Scheduler           │
│  _estimate(op)            │
│ ─ Determine relevant      │
│   capabilities (CT,       │
│   Planning, Reasoning,    │
│   Evaluation, etc.)       │
│ ─ Select strategies via   │
│   Knowledge + Experience  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    Apply Critical Thinking│
│  (pre-analysis / BVCA)    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     ActionOp.render       │
│  - instruction            │
│  - contexts               │
│  - pre-analysis           │
│  - applied strategies     │
│  - arguments              │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   Problem Solving Module  │
│  (LLM execution)          │
│  → produces result        │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Monitor              │
│  estimate_reward(op)      │
│  capability-aware scoring │
└─────────────┬─────────────┘
              │
     Reward ≥ Expected?
       ┌─────────────┐
       │   Yes       │
       ▼             │
┌─────────────┐      │
│ Record      │      │
│ execution   │      │
│ & strategies│      │
└─────────────┘      │
                     │
       ┌─────────────┴─────────────┐
       │   No (reward < expected)  │
       ▼                           │
┌───────────────────────────┐      │
│   Scheduler Replanning    │◄─────┘
│  - Feedback incorporated  │
│  - Re-select strategies   │
│    using Knowledge + LLM  │
└─────────────┬─────────────┘
              │
              ▼
     ┌─────────────────────┐
     │ Loop to Execution   │
     └─────────────────────┘



### Planning
brainary/capabilities/planning/
├── planning_base.py        # Base Planning class
│
├── # --- Cognitive / Human-like ---
├── hierarchical_planning.py   # Break down goals into subgoals (generalized HTN-style)
├── forward_planning.py        # Start from initial state, simulate toward goal
├── backward_planning.py       # Start from goal, work backwards to requirements
├── contingency_planning.py    # Plan for “what if” scenarios under uncertainty
├── opportunistic_planning.py  # Adjust plan when new opportunities arise
├── adaptive_planning.py       # Revise plan dynamically from feedback
│
├── # --- Algorithmic / Formal AI ---
├── htn_planning.py            # Hierarchical Task Networks (formalized decomposition)
├── means_end_planning.py      # Resolve gaps between current and goal states
├── critical_path_planning.py  # Optimize for dependencies & time constraints
├── mcts_planning.py           # Monte Carlo Tree Search, explore via simulation
├── default_planning.py        # Fallback strategy
