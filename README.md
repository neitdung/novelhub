# NovelHub

NovelHub is a local-first, multilingual novel analysis and wiki application.

Development begins with the repository-local AI engineering harness. Read these files in order:

1. [`PLAN.md`](PLAN.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`.agents/PROJECT.md`](.agents/PROJECT.md)
4. [`.agents/STATUS.md`](.agents/STATUS.md)

## Harness commands

```bash
make harness-check
make status
make task-check ID=NH-HARNESS-001
make check
make ci
```

The bootstrap harness uses only Python 3.11+ and GNU Make. Application toolchain commands are added phase by phase.
