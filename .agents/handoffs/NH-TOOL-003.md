# NH-TOOL-003 Developer Handoff

## Summary

Added developer quick-start commands at the top of the Makefile:

- `make start` — delegates to `scripts/start.sh`
- `make start ARGS=--local` — forwards `--local` flag
- `make stop` — delegates to `scripts/stop.sh`
- `make clear` — delegates to `scripts/clear_data.sh`

## Verification

```bash
make -n start                     # ./scripts/start.sh 
make -n start ARGS=--local        # ./scripts/start.sh --local
make -n stop                      # ./scripts/stop.sh
make -n clear                     # ./scripts/clear_data.sh
make -n harness-check             # Still passes
head -25 Makefile | grep -q start  # At top of Makefile
```

## Changed paths

| File | Change |
|------|--------|
| `Makefile` | Added `start`, `stop`, `clear` targets + `.PHONY` declarations + section header |

## Handoff

**Verdict:** Ready for QA.

PR: https://github.com/neitdung/novelhub/pull/35
