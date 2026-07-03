#!/usr/bin/env python3
"""Utilities for generating and inspecting Freeplane .mm mind maps."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

VERSION = os.environ.get("FREEPLANE_MM_VERSION", "freeplane 1.7.0")


@dataclass
class MindNode:
    text: str
    children: list["MindNode"] = field(default_factory=list)


def now_ms() -> str:
    return str(int(time.time() * 1000))


def node_to_xml(node: MindNode, timestamp: str) -> ET.Element:
    elem = ET.Element("node", {"TEXT": node.text, "CREATED": timestamp, "MODIFIED": timestamp})
    for child in node.children:
        elem.append(node_to_xml(child, timestamp))
    return elem


def write_map(root_node: MindNode, output: Path) -> None:
    timestamp = now_ms()
    root = ET.Element("map", {"version": VERSION})
    root.append(node_to_xml(root_node, timestamp))
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Freeplane 1.7 detects the dialect by checking that the file starts with <map version=...>.
    # Do not emit an XML declaration before the <map> element.
    xml = ET.tostring(root, encoding="unicode")
    output.write_text(xml + "\n", encoding="utf-8")


def normalize_markdown_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def parse_markdown(path: Path, title: str | None = None) -> MindNode:
    lines = path.read_text(encoding="utf-8").splitlines()
    root = MindNode(title or path.stem)
    # Stack entries are (logical level, node). Root level is 0.
    stack: list[tuple[int, MindNode]] = [(0, root)]

    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("<!--"):
            continue

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", raw)
        bullet = re.match(r"^(\s*)[-*+]\s+(.+?)\s*$", raw)
        numbered = re.match(r"^(\s*)\d+[.)]\s+(.+?)\s*$", raw)

        if heading:
            level = len(heading.group(1))
            text = normalize_markdown_line(heading.group(2))
        elif bullet or numbered:
            match = bullet or numbered
            indent = len(match.group(1).replace("\t", "    "))
            level = 7 + indent // 2
            text = normalize_markdown_line(match.group(2))
        else:
            level = stack[-1][0] + 1 if stack else 1
            text = normalize_markdown_line(raw)

        if not text:
            continue
        new_node = MindNode(text)
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else root
        parent.children.append(new_node)
        stack.append((level, new_node))

    if len(root.children) == 1 and not title and root.text == path.stem:
        first = root.children[0]
        if first.children:
            return first
    return root


def json_to_node(data: Any, fallback_text: str = "Mind Map") -> MindNode:
    if isinstance(data, dict) and "text" in data:
        children = [json_to_node(child, "Node") for child in data.get("children", [])]
        return MindNode(str(data.get("text") or fallback_text), children)

    if isinstance(data, dict):
        if len(data) == 1:
            key, value = next(iter(data.items()))
            return MindNode(str(key), json_children(value))
        return MindNode(fallback_text, [MindNode(str(k), json_children(v)) for k, v in data.items()])

    if isinstance(data, list):
        return MindNode(fallback_text, [json_to_node(item, "Node") for item in data])

    return MindNode(str(data))


def json_children(value: Any) -> list[MindNode]:
    if isinstance(value, list):
        return [json_to_node(item, "Node") for item in value]
    if isinstance(value, dict):
        if "text" in value:
            return [json_to_node(value)]
        return [MindNode(str(k), json_children(v)) for k, v in value.items()]
    if value is None:
        return []
    return [MindNode(str(value))]


def iter_nodes(elem: ET.Element, depth: int = 0) -> Iterable[tuple[int, ET.Element]]:
    if elem.tag == "node":
        yield depth, elem
        next_depth = depth + 1
    else:
        next_depth = depth
    for child in list(elem):
        if child.tag == "node":
            yield from iter_nodes(child, next_depth)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"]
    except OSError as exc:
        return [f"Cannot read file: {exc}"]

    root = tree.getroot()
    if root.tag != "map":
        errors.append("Root element must be <map>.")
    top_nodes = [child for child in root if child.tag == "node"]
    if not top_nodes:
        errors.append("Map must contain at least one top-level <node>.")

    for depth, node in iter_nodes(root):
        has_text = bool((node.get("TEXT") or "").strip())
        has_rich = any(child.tag == "richcontent" for child in node)
        has_child_node = any(child.tag == "node" for child in node)
        if not (has_text or has_rich or has_child_node):
            errors.append(f"Empty node at depth {depth} without TEXT, richcontent, or children.")
    return errors


def print_outline(path: Path) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    for depth, node in iter_nodes(root):
        text = (node.get("TEXT") or "").strip() or "[rich/empty node]"
        print(f"{'  ' * depth}- {text}")


def command_from_markdown(args: argparse.Namespace) -> int:
    root = parse_markdown(Path(args.input), args.title)
    write_map(root, Path(args.output))
    return 0


def command_from_json(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    root = json_to_node(data, args.title or "Mind Map")
    if args.title:
        root.text = args.title
    write_map(root, Path(args.output))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    errors = validate(Path(args.input))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OK")
    return 0


def command_outline(args: argparse.Namespace) -> int:
    print_outline(Path(args.input))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    md = sub.add_parser("from-markdown", help="Convert Markdown headings/lists to a .mm map")
    md.add_argument("input")
    md.add_argument("output")
    md.add_argument("--title")
    md.set_defaults(func=command_from_markdown)

    js = sub.add_parser("from-json", help="Convert nested JSON to a .mm map")
    js.add_argument("input")
    js.add_argument("output")
    js.add_argument("--title")
    js.set_defaults(func=command_from_json)

    val = sub.add_parser("validate", help="Validate a Freeplane .mm map")
    val.add_argument("input")
    val.set_defaults(func=command_validate)

    outline = sub.add_parser("outline", help="Print a readable outline from a .mm map")
    outline.add_argument("input")
    outline.set_defaults(func=command_outline)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
