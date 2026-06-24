from __future__ import annotations

import argparse

from common import STATUS_PATH, load_backlog, render_status


def main() -> int:
    parser = argparse.ArgumentParser(description="Render NovelHub project status")
    parser.add_argument("--write", action="store_true", help="write .agents/STATUS.md")
    args = parser.parse_args()

    rendered = render_status(load_backlog())
    if args.write:
        STATUS_PATH.write_text(rendered, encoding="utf-8")
        print(f"Wrote {STATUS_PATH}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
