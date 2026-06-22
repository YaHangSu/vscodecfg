#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path

BUILD_ROOT = Path.cwd()
OUTPUT_FILE = BUILD_ROOT.parent / "compile_commands.json"

entries = []


def read_make_var(text: str, var_name: str):
    """
    读取 qmake 多行变量：

    SOURCES = \
        a.cpp \
        b.cpp

    """
    pattern = re.compile(
        rf"^{re.escape(var_name)}\s*=\s*(.*?)^(?=[A-Za-z0-9_]+\s*=|\Z)",
        re.M | re.S,
    )

    m = pattern.search(text)
    if not m:
        return ""

    value = m.group(1)

    lines = []

    for line in value.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.endswith("\\"):
            line = line[:-1].strip()

        lines.append(line)

    return " ".join(lines)


def split_sources(source_text: str):
    result = []

    for item in source_text.split():
        if re.search(r"\.(cpp|cc|cxx|c)$", item, re.I):
            result.append(item)

    return result


for makefile in BUILD_ROOT.rglob("Makefile.Debug"):

    try:
        text = makefile.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception as e:
        print(f"skip {makefile}: {e}")
        continue

    cxxflags = read_make_var(text, "CXXFLAGS")
    defines = read_make_var(text, "DEFINES")
    incpath = read_make_var(text, "INCPATH")
    sources = read_make_var(text, "SOURCES")

    source_files = split_sources(sources)

    if not source_files:
        continue

    project_dir = makefile.parent

    flags = " ".join(
        x for x in [
            cxxflags,
            defines,
            incpath
        ] if x
    )

    for src in source_files:

        src_path = Path(src)

        if not src_path.is_absolute():
            src_path = (project_dir / src).resolve()

        entries.append({
            "directory": str(project_dir.resolve()),
            "file": str(src_path),
            "command": f"cl {flags} {src_path}"
        })

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        entries,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"generated {len(entries)} entries")
print(f"output: {OUTPUT_FILE}")