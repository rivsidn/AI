#!/usr/bin/env python3
"""Create a styled Freeplane .mm map for a directory tree."""

from __future__ import annotations

import argparse
import hashlib
import time
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "freeplane 1.7.0"
SKIP_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules", ".venv", "venv"}
SKIP_SUFFIXES = {".pyc", ".pyo"}

ZH_DESCRIPTIONS = {
    "SKILL.md": "Skill 主说明文件；定义触发场景、核心工作流和操作规范",
    "openai.yaml": "客户端界面元信息；显示名称、简短描述、默认提示词和调用策略",
    "mm-format.md": "Freeplane .mm XML 格式参考；节点属性、备注、图标、样式和安全编辑规则",
    "freeplane_mm.py": "通用 .mm 工具；Markdown/JSON 转 .mm、校验 .mm、输出可读大纲",
    "directory_map.py": "目录结构图生成器；扫描目录并输出带样式和功能标注的 Freeplane 图",
    "freeplane_screenshot.py": "可视化检查脚本；打开 Freeplane 并截屏，便于生成后查看效果",
    "Makefile": "安装、卸载和校验 Skill 的便捷命令入口",
}

EN_DESCRIPTIONS = {
    "SKILL.md": "Main skill instructions: triggers, workflows, and operating rules",
    "openai.yaml": "Client metadata: display name, short description, default prompt, and policy",
    "mm-format.md": "Freeplane .mm XML reference: node attributes, notes, icons, styles, and safe edits",
    "freeplane_mm.py": "General .mm utility: Markdown/JSON conversion, validation, and outline output",
    "directory_map.py": "Directory map generator: scans a tree and writes a styled Freeplane map",
    "freeplane_screenshot.py": "Visual check helper: opens Freeplane and captures the screen for review",
    "Makefile": "Convenience targets for installing, uninstalling, and validating the skill",
}

DIR_COLORS = ["#eadcf8", "#f4cccc", "#cfe2f3", "#d9ead3", "#fff2cc"]
FILE_COLORS = ["#f7f0ff", "#fff0f0", "#eef6ff", "#f3f9ef", "#fff8dc"]


def node_id(text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"ID_{int(digest, 16)}"


def make_node(
    text: str,
    *,
    timestamp: str,
    position: str | None = None,
    color: str | None = None,
    background: str | None = None,
    bold: bool = False,
    size: int | None = None,
    icon: str | None = None,
    children: list[ET.Element] | None = None,
) -> ET.Element:
    attrs = {
        "TEXT": text,
        "ID": node_id(text),
        "CREATED": timestamp,
        "MODIFIED": timestamp,
    }
    if children:
        attrs["FOLDED"] = "false"
        attrs["VGAP_QUANTITY"] = "8.0 pt"
    if position:
        attrs["POSITION"] = position
    if color:
        attrs["COLOR"] = color
    if background:
        attrs["BACKGROUND_COLOR"] = background
    attrs.setdefault("MAX_WIDTH", "520.0 px")
    elem = ET.Element("node", attrs)
    if icon:
        ET.SubElement(elem, "icon", {"BUILTIN": icon})
    if bold or size:
        font_attrs = {}
        if bold:
            font_attrs["BOLD"] = "true"
        if size:
            font_attrs["SIZE"] = str(size)
        ET.SubElement(elem, "font", font_attrs)
    for child in children or []:
        elem.append(child)
    return elem


def load_descriptions(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--describe must use NAME=TEXT, got: {value}")
        name, text = value.split("=", 1)
        result[name.strip()] = text.strip()
    return result


def default_description(path: Path, lang: str, custom: dict[str, str]) -> str:
    if path.name in custom:
        return custom[path.name]
    descriptions = ZH_DESCRIPTIONS if lang == "zh" else EN_DESCRIPTIONS
    if path.name in descriptions:
        return descriptions[path.name]
    if path.is_dir():
        return "目录" if lang == "zh" else "Directory"
    suffix = path.suffix.lower()
    if lang == "zh":
        if suffix == ".md":
            return "Markdown 文档或参考说明"
        if suffix in {".yaml", ".yml", ".json", ".toml"}:
            return "配置或结构化数据文件"
        if suffix == ".py":
            return "Python 自动化脚本"
        if suffix == ".mm":
            return "Freeplane 思维导图文件"
        return "项目文件"
    if suffix == ".md":
        return "Markdown documentation or reference"
    if suffix in {".yaml", ".yml", ".json", ".toml"}:
        return "Configuration or structured data file"
    if suffix == ".py":
        return "Python automation script"
    if suffix == ".mm":
        return "Freeplane mind map file"
    return "Project file"


def should_skip(path: Path, include_hidden: bool) -> bool:
    if path.is_dir() and path.name in SKIP_DIRS:
        return True
    if path.suffix in SKIP_SUFFIXES:
        return True
    if not include_hidden and path.name.startswith("."):
        return True
    return False


def build_tree(
    path: Path,
    *,
    root: Path,
    timestamp: str,
    lang: str,
    custom: dict[str, str],
    max_depth: int,
    depth: int = 0,
    position: str | None = None,
    include_hidden: bool = False,
) -> ET.Element:
    rel = "." if path == root else str(path.relative_to(root))
    desc = default_description(path, lang, custom)
    label_name = f"{path.name}/" if path.is_dir() else path.name
    text = f"{label_name}\n{desc}" if path != root else f"{path.name}/\n{desc}\n{path}"

    children: list[ET.Element] = []
    if path.is_dir() and depth < max_depth:
        entries = sorted(
            [p for p in path.iterdir() if not should_skip(p, include_hidden)],
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
        for index, child in enumerate(entries):
            child_position = None
            if depth == 0:
                child_position = "right" if index % 2 == 0 else "left"
            children.append(
                build_tree(
                    child,
                    root=root,
                    timestamp=timestamp,
                    lang=lang,
                    custom=custom,
                    max_depth=max_depth,
                    depth=depth + 1,
                    position=child_position,
                    include_hidden=include_hidden,
                )
            )

    if path == root:
        return make_node(
            text,
            timestamp=timestamp,
            background="#fff2cc",
            color="#1f2933",
            bold=True,
            size=16,
            icon="bookmark",
            children=children,
        )
    if path.is_dir():
        return make_node(
            text,
            timestamp=timestamp,
            position=position,
            background=DIR_COLORS[depth % len(DIR_COLORS)],
            bold=True,
            icon="folder",
            children=children,
        )
    icon = "executable" if path.suffix == ".py" else "info"
    return make_node(
        text,
        timestamp=timestamp,
        position=position,
        background=FILE_COLORS[depth % len(FILE_COLORS)],
        icon=icon,
        children=children,
    )


def write_directory_map(args: argparse.Namespace) -> None:
    root_dir = Path(args.directory).expanduser().resolve()
    if not root_dir.is_dir():
        raise SystemExit(f"Not a directory: {root_dir}")
    timestamp = str(int(time.time() * 1000))
    custom = load_descriptions(args.describe or [])
    map_elem = ET.Element("map", {"version": args.version})
    root_node = build_tree(
        root_dir,
        root=root_dir,
        timestamp=timestamp,
        lang=args.lang,
        custom=custom,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
    )
    if args.title:
        root_node.set("TEXT", f"{args.title}\n{root_dir}")
    map_elem.append(root_node)
    tree = ET.ElementTree(map_elem)
    ET.indent(tree, space="  ")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(ET.tostring(map_elem, encoding="unicode") + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("output", help="Output .mm file")
    parser.add_argument("--title", help="Override root node title")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Description language")
    parser.add_argument("--max-depth", type=int, default=4, help="Maximum directory depth to include")
    parser.add_argument("--include-hidden", action="store_true", help="Include dotfiles and dot directories")
    parser.add_argument("--describe", action="append", help="Custom description as NAME=TEXT; repeatable")
    parser.add_argument("--version", default=VERSION, help="Freeplane map version string")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    write_directory_map(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
