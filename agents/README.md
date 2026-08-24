# agents

LOOM agent instructions are rooted at `/AGENTS.md`.

For Pi, future prompts should normally be compact work packages that inherit `/AGENTS.md` rather than restating project history.

Minimal pattern:

```text
Read AGENTS.md.
LOOM WP <id>
Goal: ...
Inputs: ...
Change: ...
Gates: ...
Evidence: ...
Return: ...
STOP
```

Only add context that differs from, or is not already present in, `AGENTS.md`.
