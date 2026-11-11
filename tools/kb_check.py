#!/usr/bin/env python3
"""Check the trace data of a Kokeb board repository (Python 3.9+, PyYAML).

    python3 tools/kb_check.py                  # check the repository in the current directory
    python3 tools/kb_check.py --report build   # also write build/trace-report.json and build/trace-report.md

The trace data lives in trace/*.yml (see trace/SCHEMA.md): needs, requirements, risks and verifications, each a
list of items with an ID, a version and links to the items they come from. The check fails (exit 1) on any error:
a broken link, a missing parent, an approved requirement nobody verifies, and every *suspect* link, that is a link
recorded against an older version of its target. Warnings do not fail the check.

This is the version-0 copy shipped with board-template; it moves into kokeb-labs/ci-tools once it is stable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("kb_check.py needs PyYAML: python3 -m pip install pyyaml")

FILES = {
    "need": "needs.yml",
    "requirement": "requirements.yml",
    "risk": "risks.yml",
    "verification": "verification.yml",
}
PREFIX = {"need": "N", "requirement": "R", "risk": "H", "verification": "V"}
ID_RE = re.compile(r"^([NRHV])-(\d{3,})$")
CLASSES = ("public", "internal", "confidential", "restricted")

COMMON = ("id", "title", "status", "version", "classification")
REQUIRED = {
    "need": COMMON + ("statement", "stakeholder", "source"),
    "requirement": COMMON + ("statement", "rationale", "kind", "derives_from"),
    "risk": COMMON + ("hazard", "harm", "controls"),
    "verification": COMMON + ("method", "verifies"),
}
ENUMS = {
    ("need", "status"): ("draft", "accepted", "rejected", "deferred", "superseded"),
    ("requirement", "status"): ("draft", "approved", "rejected", "superseded"),
    ("requirement", "kind"): ("system", "electrical", "software", "mechanical", "manufacturing", "documentation"),
    ("risk", "status"): ("open", "controlled", "accepted", "closed"),
    ("verification", "status"): ("planned", "passed", "failed", "waived"),
    ("verification", "method"): ("test", "inspection", "analysis", "demonstration"),
}
# Which item types each link field may point at.
LINKS = {
    ("requirement", "derives_from"): ("need", "requirement"),
    ("risk", "controls"): ("requirement",),
    ("verification", "verifies"): ("requirement",),
}
DEAD = ("rejected", "superseded")


class Finding:
    def __init__(self, level: str, code: str, item: str, message: str) -> None:
        self.level, self.code, self.item, self.message = level, code, item, message

    def __str__(self) -> str:
        where = f" {self.item}:" if self.item else ""
        return f"{self.level.upper():<7} {self.code}{where} {self.message}"

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "item": self.item, "message": self.message}


def load_items(trace: Path, findings: list[Finding]) -> dict[str, dict[str, Any]]:
    """Read every trace file; returns {id: item} with the item's type added as `_type`."""
    items: dict[str, dict[str, Any]] = {}
    for kind, name in FILES.items():
        path = trace / name
        if not path.is_file():
            findings.append(Finding("error", "K001", "", f"trace/{name} is missing"))
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            findings.append(Finding("error", "K001", "", f"trace/{name} is not valid YAML: {exc}"))
            continue
        if data is None:
            data = []
        if not isinstance(data, list):
            findings.append(Finding("error", "K001", "", f"trace/{name} must be a list of items"))
            continue
        for pos, item in enumerate(data, 1):
            if not isinstance(item, dict):
                findings.append(Finding("error", "K001", "", f"trace/{name} entry {pos} is not a mapping"))
                continue
            item_id = str(item.get("id", f"{name}#{pos}"))
            m = ID_RE.match(item_id)
            if not m or m.group(1) != PREFIX[kind]:
                findings.append(Finding("error", "K003", item_id,
                                        f"id must look like {PREFIX[kind]}-001 in trace/{name}"))
            if item_id in items:
                findings.append(Finding("error", "K002", item_id, "duplicate id"))
                continue
            item["_type"] = kind
            items[item_id] = item
    return items


def link_list(item: dict[str, Any], field: str) -> list[Any]:
    value = item.get(field)
    return value if isinstance(value, list) else []


def check_fields(item_id: str, item: dict[str, Any], allowed: tuple[str, ...], findings: list[Finding]) -> None:
    kind = item["_type"]
    for field in REQUIRED[kind]:
        value = item.get(field)
        if value is None or value == "" or value == []:
            findings.append(Finding("error", "K004", item_id, f"missing required field '{field}'"))
    for field in ("status", "kind", "method"):
        allowed_values = ENUMS.get((kind, field))
        if allowed_values and item.get(field) is not None and item[field] not in allowed_values:
            findings.append(Finding("error", "K005", item_id,
                                    f"{field} '{item[field]}' is not one of {', '.join(allowed_values)}"))
    version = item.get("version")
    if version is not None and (not isinstance(version, int) or isinstance(version, bool) or version < 1):
        findings.append(Finding("error", "K015", item_id, "version must be a whole number from 1"))
    cls = item.get("classification")
    if cls is not None and cls not in CLASSES:
        findings.append(Finding("error", "K005", item_id, f"classification '{cls}' is not one of {', '.join(CLASSES)}"))
    elif cls is not None and cls not in allowed:
        findings.append(Finding("error", "K006", item_id,
                                f"classification '{cls}' is not allowed in this repository (allowed: "
                                f"{', '.join(allowed)}); restricted content does not belong in an open board"))
    if kind == "need":
        src = item.get("source")
        if src is not None and not (isinstance(src, dict) and src.get("kind") and src.get("ref")):
            findings.append(Finding("error", "K004", item_id, "source needs 'kind' and 'ref'"))
    if item.get("example"):
        findings.append(Finding("warn", "K014", item_id, "example item: replace or delete it before a release"))


def check_links(items: dict[str, dict[str, Any]], findings: list[Finding]) -> None:
    for item_id, item in items.items():
        kind = item["_type"]
        for (src_kind, field), targets in LINKS.items():
            if src_kind != kind:
                continue
            for link in link_list(item, field):
                if not (isinstance(link, dict) and "id" in link and "ver" in link):
                    findings.append(Finding("error", "K007", item_id,
                                            f"{field} entries must look like {{id: R-001, ver: 1}}"))
                    continue
                target = items.get(str(link["id"]))
                if target is None:
                    findings.append(Finding("error", "K007", item_id,
                                            f"{field} points at {link['id']}, which does not exist"))
                    continue
                if target["_type"] not in targets:
                    findings.append(Finding("error", "K007", item_id,
                                            f"{field} may point at {' or '.join(targets)}, not at {link['id']} "
                                            f"({target['_type']})"))
                    continue
                tv, lv = target.get("version"), link["ver"]
                if isinstance(tv, int) and isinstance(lv, int):
                    if lv < tv:
                        findings.append(Finding("error", "K008", item_id,
                                                f"suspect link: {link['id']} is at version {tv} but {field} records "
                                                f"{lv}; review {item_id} against the change, then set ver: {tv}"))
                    elif lv > tv:
                        findings.append(Finding("error", "K008", item_id,
                                                f"{field} records {link['id']} version {lv}, which does not exist "
                                                f"(current is {tv})"))
                if target.get("status") in DEAD and item.get("status") not in DEAD:
                    findings.append(Finding("error", "K013", item_id,
                                            f"{field} points at {link['id']}, which is {target['status']}"))


def check_rules(items: dict[str, dict[str, Any]], findings: list[Finding]) -> None:
    verified: dict[str, list[dict[str, Any]]] = {}
    for item in items.values():
        if item["_type"] == "verification":
            for link in link_list(item, "verifies"):
                if isinstance(link, dict):
                    verified.setdefault(str(link.get("id")), []).append(item)
    for item_id, item in items.items():
        kind = item["_type"]
        if kind == "requirement" and item.get("status") == "approved":
            if not verified.get(item_id) and not item.get("verification_waiver"):
                findings.append(Finding("error", "K010", item_id,
                                        "approved requirement has no verification and no verification_waiver"))
        if kind == "verification" and item.get("status") == "passed" and not item.get("evidence"):
            findings.append(Finding("error", "K011", item_id, "a passed verification must list its evidence"))
        if kind == "verification" and item.get("status") == "waived" and not item.get("waiver"):
            findings.append(Finding("error", "K011", item_id, "a waived verification must give the waiver reason"))
        if kind == "risk" and item.get("status") in ("controlled", "closed") and not link_list(item, "controls"):
            findings.append(Finding("error", "K012", item_id, "a controlled risk needs at least one control"))


def coverage(items: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reqs = {k: v for k, v in items.items() if v["_type"] == "requirement" and v.get("status") not in DEAD}
    vers = [v for v in items.values() if v["_type"] == "verification"]
    status_of: dict[str, list[str]] = {}
    for ver in vers:
        for link in link_list(ver, "verifies"):
            if isinstance(link, dict):
                status_of.setdefault(str(link.get("id")), []).append(str(ver.get("status")))
    rows = []
    for rid, req in sorted(reqs.items()):
        states = status_of.get(rid, [])
        if states and all(s in ("passed", "waived") for s in states):
            state = "verified"
        elif "failed" in states:
            state = "failed"
        elif states:
            state = "planned"
        else:
            state = "waived" if req.get("verification_waiver") else "unverified"
        rows.append({"id": rid, "title": req.get("title"), "status": req.get("status"), "verification": state})
    counts = {s: sum(1 for r in rows if r["verification"] == s)
              for s in ("verified", "planned", "failed", "waived", "unverified")}
    return {"requirements": rows, "counts": counts, "total": len(rows),
            "items": {t: sum(1 for v in items.values() if v["_type"] == t) for t in FILES}}


def write_report(out: Path, cov: dict[str, Any], findings: list[Finding]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    payload = {"coverage": cov, "findings": [f.as_dict() for f in findings]}
    (out / "trace-report.json").write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    summary = ", ".join(f"{n} {s}" for s, n in cov["counts"].items() if n)
    lines = ["# Trace report", "", f"Requirements: {cov['total']}. {summary}.", "",
             "| Requirement | Title | Status | Verification |", "| --- | --- | --- | --- |"]
    for r in cov["requirements"]:
        lines.append(f"| {r['id']} | {r['title']} | {r['status']} | {r['verification']} |")
    errors = [f for f in findings if f.level == "error"]
    lines += ["", f"Findings: {len(errors)} error(s), {len(findings) - len(errors)} warning(s).", ""]
    lines += [f"- `{f.code}` {f.item} {f.message}" for f in findings]
    (out / "trace-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(root: Path) -> tuple[dict[str, dict[str, Any]], list[Finding]]:
    findings: list[Finding] = []
    allowed: tuple[str, ...] = ("public",)
    board = root / "board.yml"
    if board.is_file():
        try:
            cfg = yaml.safe_load(board.read_text(encoding="utf-8")) or {}
            allowed = tuple(cfg.get("allowed_classifications", allowed))
        except yaml.YAMLError as exc:
            findings.append(Finding("error", "K001", "", f"board.yml is not valid YAML: {exc}"))
    else:
        findings.append(Finding("error", "K001", "", "board.yml is missing"))
    items = load_items(root / "trace", findings)
    for item_id, item in items.items():
        check_fields(item_id, item, allowed, findings)
    check_links(items, findings)
    check_rules(items, findings)
    return items, findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."), help="repository root (default: current directory)")
    ap.add_argument("--report", type=Path, help="write trace-report.json and trace-report.md to this folder")
    args = ap.parse_args(argv)
    items, findings = run(args.root)
    cov = coverage(items)
    for f in findings:
        print(f)
    errors = sum(1 for f in findings if f.level == "error")
    c = cov["counts"]
    print(f"\n{len(items)} items; requirements: {cov['total']} ({c['verified']} verified, {c['planned']} planned, "
          f"{c['failed']} failed, {c['waived']} waived, {c['unverified']} unverified); "
          f"{errors} error(s), {len(findings) - errors} warning(s).")
    if args.report:
        write_report(args.report, cov, findings)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
