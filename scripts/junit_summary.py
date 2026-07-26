"""Turn a JUnit XML file into a markdown table for the GitHub Actions run page.

GitHub renders whatever is appended to the file named by ``$GITHUB_STEP_SUMMARY``
directly on the workflow run page. That makes it the cheapest reporting surface
there is: no hosting, no branch, no extra service -- and it is the only one a
reviewer sees without clicking anything.

Usage:
    python scripts/junit_summary.py junit.xml "API tests"

Writes to ``$GITHUB_STEP_SUMMARY`` when set, otherwise stdout, so the same
command is useful locally.
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _suites(root: ET.Element) -> list[ET.Element]:
    """Handle both shapes: <testsuites><testsuite> and a bare <testsuite>."""
    return (
        [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    )


def summarise(xml_path: Path, title: str) -> str:
    if not xml_path.exists():
        return f"## {title}\n\n> No JUnit XML found at `{xml_path}` -- the run probably died before tests started.\n"

    root = ET.parse(xml_path).getroot()

    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "time": 0.0}
    for suite in _suites(root):
        for key in ("tests", "failures", "errors", "skipped"):
            totals[key] += int(suite.get(key, 0) or 0)
        totals["time"] += float(suite.get("time", 0) or 0)

    failed = totals["failures"] + totals["errors"]
    passed = totals["tests"] - failed - totals["skipped"]
    icon = "❌" if failed else ("⚠️" if totals["skipped"] and not totals["tests"] else "✅")

    lines = [
        f"## {icon} {title}",
        "",
        "| Result | Count |",
        "| :--- | ---: |",
        f"| ✅ Passed | {passed} |",
        f"| ❌ Failed | {failed} |",
        f"| ⏭️ Skipped | {totals['skipped']} |",
        f"| **Total** | **{totals['tests']}** |",
        "",
        f"_Duration: {totals['time']:.2f}s_",
        "",
    ]

    # Only enumerate failures. A list of every passing test is noise -- the
    # point of this surface is to answer "what broke?" without leaving the page.
    if failed:
        lines += ["<details><summary>Failed tests</summary>", ""]
        for suite in _suites(root):
            for case in suite.iter("testcase"):
                problems = list(case.findall("failure")) + list(case.findall("error"))
                if not problems:
                    continue
                name = f"{case.get('classname', '')}::{case.get('name', '')}".strip(":")
                message = (problems[0].get("message") or "").strip().splitlines()
                first_line = message[0] if message else "no message"
                lines.append(f"- **{name}**")
                lines.append(f"  - `{first_line[:300]}`")
        lines += ["", "</details>", ""]

    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    xml_path = Path(sys.argv[1])
    title = sys.argv[2] if len(sys.argv) > 2 else xml_path.stem

    markdown = summarise(xml_path, title)

    destination = os.getenv("GITHUB_STEP_SUMMARY")
    if destination:
        with open(destination, "a", encoding="utf-8") as handle:
            handle.write(markdown + "\n")
    else:
        print(markdown)

    # Always exit 0. This script reports on the run; it must not be the thing
    # that decides whether the run passed -- pytest already did that.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
