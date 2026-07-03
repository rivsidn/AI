---
name: freeplane
description: Create, edit, inspect, validate, screenshot-check, and export Freeplane mind maps in .mm XML format. Use when the user asks to generate a Freeplane mind map, draw a directory structure map with file/function labels, convert Markdown/JSON/outline text into a .mm file, modify nodes/styles/icons/links/notes in an existing .mm file, validate whether a .mm file can be opened by Freeplane, visually inspect a generated map via screenshot, or automate Freeplane on Linux.
---

# Freeplane

## Core workflow

1. Identify the target operation: create a new `.mm`, convert from an outline/Markdown/JSON source, edit an existing `.mm`, inspect structure, validate, or export with the `freeplane` CLI.
2. Prefer deterministic XML generation/editing over GUI automation. Freeplane `.mm` files are XML; use Python XML tooling and preserve valid structure.
3. Use `scripts/freeplane_mm.py` for common operations:
   - `from-markdown INPUT.md OUTPUT.mm` to convert Markdown headings/lists into a Freeplane map.
   - `from-json INPUT.json OUTPUT.mm` to convert a nested JSON tree into a Freeplane map.
   - `outline INPUT.mm` to print a readable outline from a map.
   - `validate INPUT.mm` to check XML structure and required Freeplane elements.
4. Use `scripts/directory_map.py DIR OUTPUT.mm` when the user asks for a directory/file structure picture with file-purpose labels.
5. Use `scripts/freeplane_screenshot.py MAP.mm screenshot.png` when a GUI display is available and the user wants the generate-and-view feedback loop. Inspect the PNG and iterate on layout/style if needed.
6. Read `references/mm-format.md` when adding advanced features such as styles, notes, links, icons, folded nodes, or custom node attributes.
7. If the user wants a visual/exported result, check whether `freeplane` exists with `command -v freeplane`; then run Freeplane export only when a display/headless environment supports it. Always keep the `.mm` source as the primary artifact.

## Creating maps

- Set the root node text to the user-facing title.
- Represent hierarchy with nested `<node TEXT="...">` elements.
- Include `version="freeplane 1.7.0"` or another installed-compatible version on `<map>`; allow `FREEPLANE_MM_VERSION` overrides when using the bundled script.
- Add stable timestamps in milliseconds to `CREATED` and `MODIFIED` if useful; exact timestamps are not semantically important.
- Escape XML through an XML library, not string concatenation.
- Do not emit an XML declaration before `<map>` for Freeplane 1.7 compatibility; its dialect detector expects the file to start with `<map version="...">`.
- Keep generated maps simple unless the user asks for styling; Freeplane can open minimal `.mm` XML reliably.

Example minimal structure:

```xml
<map version="freeplane 1.7.0">
  <node TEXT="Root">
    <node TEXT="Child" />
  </node>
</map>
```

## Directory structure maps

Use the styled directory-map workflow for requests like "draw this folder", "show the project tree", or "mark each file's function".

Run:

```bash
python3 path/to/freeplane/scripts/directory_map.py /path/to/dir output.mm --title "Project Structure"
python3 path/to/freeplane/scripts/freeplane_mm.py validate output.mm
```

The generated map should:

- use a central root node with the absolute directory path;
- place first-level children on both left and right to keep the screenshot compact;
- use colored directory/file nodes, icons, and `FOLDED="false"` for readable screenshots;
- label each node as `name` plus a short function/role line;
- accept `--describe NAME=TEXT` overrides when the default file-purpose description is not specific enough.

## Visual inspection loop

When a display is available and the user cares about visual effect, validate by actually opening Freeplane and capturing a screenshot.

```bash
python3 path/to/freeplane/scripts/freeplane_screenshot.py output.mm /tmp/output.png --wait 7
```

Then inspect `/tmp/output.png` with the available image-viewing tool. Iterate if the map is too sparse, cramped, folded, off-center, or shows a Freeplane warning dialog. A Freeplane 1.7 "unknown program" warning usually means the file does not start directly with `<map version="freeplane 1.7.0">`.

## Editing existing maps

- Parse with `xml.etree.ElementTree` or `lxml` if available.
- Preserve unknown Freeplane elements/attributes where possible; Freeplane stores styles, icons, notes, hooks, and extensions as XML children.
- Modify only nodes relevant to the request. Do not reformat unrelated large maps unless needed.
- After editing, run `scripts/freeplane_mm.py validate FILE.mm` and, if possible, open/export with Freeplane for a stronger check.

## Markdown conversion conventions

- Heading levels (`#`, `##`, `###`) become hierarchy levels.
- Bullet indentation creates child nodes under the current heading/list parent.
- Plain paragraphs are appended as nodes under the nearest heading.
- For predictable results, ask the user for clarification only when the intended hierarchy cannot be reasonably inferred.

## JSON conversion conventions

`scripts/freeplane_mm.py from-json` accepts either:

```json
{"text": "Root", "children": [{"text": "Child"}]}
```

or a shorthand mapping/list structure:

```json
{"Root": {"Branch": ["Leaf A", "Leaf B"]}}
```

## Validation

Run:

```bash
python3 path/to/freeplane/scripts/freeplane_mm.py validate map.mm
```

Validation should confirm:

- the file is well-formed XML;
- the root element is `<map>`;
- there is at least one top-level `<node>`;
- every node has either `TEXT`, rich content, or child nodes.

## Linux Freeplane notes

- Launch GUI: `freeplane file.mm`.
- Check installation: `command -v freeplane`.
- Avoid relying on GUI commands in non-interactive sessions. If export fails due to display/headless constraints, report that the `.mm` was created/validated and explain how the user can open it locally.
