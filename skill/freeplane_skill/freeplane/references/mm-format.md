# Freeplane .mm Format Notes

Use this reference when a task needs details beyond a simple generated map.

## Basic XML

A Freeplane map is XML with a `<map>` root and nested `<node>` elements:

```xml
<map version="freeplane 1.12.1">
  <node TEXT="Topic">
    <node TEXT="Subtopic" />
  </node>
</map>
```

Common node attributes:

- `TEXT`: visible plain-text label.
- `CREATED`, `MODIFIED`: Unix epoch milliseconds.
- `ID`: optional node identifier, often `ID_` plus digits.
- `POSITION`: usually `left` or `right` for direct children of the root.
- `FOLDED`: `true` to collapse a branch.
- `LINK`: URL or file link.
- `STYLE`: style name such as `bubble`, `fork`, or a custom style defined in the map.

## Notes and rich content

Freeplane may store notes and rich text as child XML extensions. Preserve unknown children when editing existing files.

A simple note can be represented as richcontent:

```xml
<richcontent TYPE="NOTE">
  <html><head></head><body><p>Note text</p></body></html>
</richcontent>
```

Prefer plain `TEXT` nodes for generated content unless the user asks for notes or HTML formatting.

## Icons

Icons are children of a node:

```xml
<icon BUILTIN="idea" />
```

Common built-ins include `idea`, `button_ok`, `button_cancel`, `bookmark`, `flag`, `messagebox_warning`, `yes`, and `help`.

## Styling

Simple generated maps usually do not need style definitions. For lightweight emphasis, set node attributes or add children:

```xml
<node TEXT="Important" STYLE="bubble">
  <font BOLD="true" />
</node>
```

Common font attributes: `BOLD="true"`, `ITALIC="true"`, `SIZE="14"`, `NAME="SansSerif"`.

Colors are hex RGB strings such as `#ffcc00`:

```xml
<node TEXT="Risk" BACKGROUND_COLOR="#ffe1e1" COLOR="#8a0000" />
```

## Safe editing rules

- Use an XML parser; never build user content through raw XML string interpolation.
- Preserve children named `hook`, `richcontent`, `attribute`, `icon`, `cloud`, `arrowlink`, and unknown extension nodes.
- Do not remove map-level style definitions unless explicitly requested.
- Validate after edits and keep a backup when modifying an existing user file in place.
