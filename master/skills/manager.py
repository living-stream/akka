from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


@dataclass(frozen=True)
class SkillMeta:
    name: str
    description: str
    tags: tuple[str, ...]
    triggers: tuple[str, ...]
    tools: tuple[str, ...]
    skill_dir: Path
    skill_md_path: Path


class SkillIndex:
    def __init__(self, skills_root: Path | None = None):
        if skills_root:
            self.skills_root = skills_root
        else:
            self.skills_root = Path(__file__).parent / "definitions"

    def discover(self) -> dict[str, SkillMeta]:
        if not self.skills_root.exists():
            return {}

        metas: dict[str, SkillMeta] = {}
        for skill_dir in sorted([p for p in self.skills_root.iterdir() if p.is_dir()]):
            skill_md_path = skill_dir / "SKILL.md"
            if not skill_md_path.exists():
                continue
            try:
                meta = self._load_meta(skill_md_path=skill_md_path)
            except Exception:
                continue
            if meta.name not in metas:
                metas[meta.name] = meta
        return metas

    def read_skill_markdown(self, name: str) -> str:
        metas = self.discover()
        if name not in metas:
            raise FileNotFoundError(f"Skill not found: {name}")
        return metas[name].skill_md_path.read_text(encoding="utf-8")

    def read_skill_file(self, name: str, relative_path: str) -> str:
        metas = self.discover()
        if name not in metas:
            raise FileNotFoundError(f"Skill not found: {name}")

        skill_dir = metas[name].skill_dir.resolve()
        target = (skill_dir / relative_path).resolve()
        if skill_dir not in target.parents and target != skill_dir:
            raise ValueError("Path escapes skill directory")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Skill file not found: {name}/{relative_path}")

        return target.read_text(encoding="utf-8")

    def build_manifest_text(self, metas: dict[str, SkillMeta] | None = None) -> str:
        if metas is None:
            metas = self.discover()
        if not metas:
            return ""

        lines: list[str] = []
        lines.append("可用 Skills（按需加载，匹配触发词后自动加载详细流程）：")
        for meta in sorted(metas.values(), key=lambda m: m.name):
            desc = meta.description.strip().replace("\n", " ")
            triggers_str = "、".join(meta.triggers[:3])
            lines.append(f"- {meta.name}: {desc}")
            lines.append(f"  触发词: {triggers_str}")
        return "\n".join(lines).strip()

    def find_triggered_skills(self, task: str, metas: dict[str, SkillMeta] | None = None) -> list[SkillMeta]:
        if metas is None:
            metas = self.discover()
        task_text = (task or "").lower()
        matched: list[SkillMeta] = []
        for meta in metas.values():
            if any(trigger.lower() in task_text for trigger in meta.triggers):
                matched.append(meta)
        return sorted(matched, key=lambda m: m.name)

    def _load_meta(self, skill_md_path: Path) -> SkillMeta:
        content = skill_md_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        name = str(frontmatter.get("name", "")).strip()
        description = str(frontmatter.get("description", "")).strip()
        tags = _coerce_str_list(frontmatter.get("tags", []))
        triggers = _coerce_str_list(frontmatter.get("triggers", []))
        tools = _coerce_str_list(frontmatter.get("tools", []))

        if not name or not _SKILL_NAME_RE.match(name):
            raise ValueError("Invalid or missing skill name")
        if not description:
            raise ValueError("Missing skill description")

        return SkillMeta(
            name=name,
            description=description,
            tags=tuple(tags),
            triggers=tuple(triggers),
            tools=tuple(tools),
            skill_dir=skill_md_path.parent,
            skill_md_path=skill_md_path,
        )


class MemoryManager:
    def __init__(self, memory_paths: list[str | Path] | None = None):
        self.memory_paths = [Path(p) if isinstance(p, str) else p for p in (memory_paths or [])]

    def load_memories(self) -> str:
        contents: list[str] = []
        for path in self.memory_paths:
            if path.exists() and path.is_file():
                try:
                    content = path.read_text(encoding="utf-8").strip()
                    if content:
                        contents.append(f"<!-- Source: {path} -->\n{content}")
                except Exception:
                    continue
        return "\n\n---\n\n".join(contents) if contents else ""

    def add_memory_path(self, path: str | Path) -> None:
        p = Path(path) if isinstance(path, str) else path
        if p not in self.memory_paths:
            self.memory_paths.append(p)


def parse_frontmatter(markdown: str) -> dict[str, Any]:
    text = markdown.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    yaml_lines: list[str] = []
    end_index: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
        yaml_lines.append(lines[i])

    if end_index is None:
        return {}

    return _parse_yaml_like("\n".join(yaml_lines))


def _parse_yaml_like(yaml_text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    list_acc: list[str] | None = None

    for raw_line in yaml_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue

        stripped = line.lstrip()
        if stripped.startswith("- "):
            if current_key is None or list_acc is None:
                continue
            list_acc.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        current_key = key

        if value == "":
            list_acc = []
            data[key] = list_acc
            continue

        list_acc = None
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                data[key] = []
            else:
                parts = [p.strip() for p in inner.split(",")]
                data[key] = [p.strip().strip('"').strip("'") for p in parts if p]
            continue

        data[key] = value.strip().strip('"').strip("'")

    return data


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        v = value.strip()
        return [v] if v else []
    return [str(value).strip()] if str(value).strip() else []
