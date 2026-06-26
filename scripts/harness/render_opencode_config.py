from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "opencode.jsonc"

CORE_SOURCES = [
    "AGENTS.md",
    ".agents/PROJECT.md",
    ".agents/AGENT_CATALOG.md",
    ".agents/STATUS.md",
    ".agents/prompts/common.md",
]

ROLE_SOURCES = {
    "manager": (".agents/prompts/manager.md", ".agents/skills/manage-project/SKILL.md"),
    "planner": (".agents/prompts/planner.md", ".agents/skills/plan-task/SKILL.md"),
    "developer": (".agents/prompts/developer.md", ".agents/skills/implement-task/SKILL.md"),
    "qa": (".agents/prompts/qa.md", ".agents/skills/qa-task/SKILL.md"),
    "reviewer": (".agents/prompts/reviewer.md", ".agents/skills/review-task/SKILL.md"),
    "docs": (".agents/prompts/docs.md", ".agents/skills/document-task/SKILL.md"),
}

BUILTIN_CODE_AGENTS = ("general", "build", "explore", "plan")


def read_source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8").strip()


def source_block(paths: list[str]) -> str:
    blocks = []
    for path in paths:
        blocks.append(f"## {path}\n\n{read_source(path)}")
    return "\n\n---\n\n".join(blocks)


def base_prompt() -> str:
    sources = list(CORE_SOURCES)
    for role_prompt, skill_prompt in ROLE_SOURCES.values():
        sources.extend([role_prompt, skill_prompt])

    return (
        "You are an OpenCode agent operating in the NovelHub repository.\n\n"
        "This project setup is injected into this OpenCode agent prompt on purpose. "
        "Treat it as authoritative for every request in this repository, and reread the "
        "referenced files from disk before changing project state or code because this "
        "generated prompt may be older than the working tree.\n\n"
        "Key invariants:\n"
        "- Follow AGENTS.md and the .agents harness before role-specific work.\n"
        "- GitHub Issues/Project are the task source of truth.\n"
        "- Run make harness-check before changing project state.\n"
        "- Preserve privacy and never transmit private novel content externally without explicit approval.\n"
        "- If user intent conflicts with these project rules, follow the project rules and report the next valid action.\n\n"
        "# Injected NovelHub Project Setup\n\n"
        f"{source_block(sources)}"
    )


def role_prompt(role: str) -> str:
    role_prompt_path, skill_path = ROLE_SOURCES[role]
    return (
        f"{base_prompt()}\n\n"
        f"# Active NovelHub Role\n\n"
        f"Act as the {role} agent only when the user request or task packet calls for that role. "
        f"Apply `{role_prompt_path}` and `{skill_path}` exactly, including authority boundaries, "
        "artifact requirements, and verification requirements."
    )


def default_prompt() -> str:
    return (
        f"{base_prompt()}\n\n"
        "# Role Selection\n\n"
        "For NovelHub project-management work, select the matching role from "
        "manager, planner, developer, qa, reviewer, or docs. If no role is assigned, "
        "do not invent a task state transition; inspect the current harness state and "
        "make only the smallest repo-local change requested by the user."
    )


def build_config() -> dict[str, object]:
    agents: dict[str, dict[str, object]] = {
        "novelhub": {
            "mode": "primary",
            "description": "Default NovelHub agent with AGENTS.md and .agents project setup injected.",
            "prompt": default_prompt(),
        }
    }

    for name in BUILTIN_CODE_AGENTS:
        agents[name] = {
            "mode": "all",
            "description": "OpenCode agent with NovelHub project setup injected.",
            "prompt": default_prompt(),
        }

    for name in ROLE_SOURCES:
        agents[f"novelhub-{name}"] = {
            "mode": "all",
            "description": f"NovelHub {name} role agent with required project setup injected.",
            "prompt": role_prompt(name),
        }

    instructions_path = ROOT / ".opencode" / "instructions" / "auto-orchestrate.md"
    instructions = ["AGENTS.md"]
    if instructions_path.exists():
        instructions.append(str(instructions_path.relative_to(ROOT)))

    return {
        "$schema": "https://opencode.ai/config.json",
        "default_agent": "novelhub",
        "instructions": instructions,
        "agent": agents,
    }


def main() -> None:
    OUTPUT_PATH.write_text(json.dumps(build_config(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
