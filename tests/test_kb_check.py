"""Tests for tools/kb_check.py: run with `python3 -m unittest discover -s tests`."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import kb_check  # noqa: E402


def item(prefix: str, n: int, **extra) -> dict:
    base = {"id": f"{prefix}-{n:03d}", "title": "t", "status": "draft", "version": 1, "classification": "public"}
    base.update(extra)
    return base


def need(n=1, **kw):
    return item("N", n, statement="s", stakeholder="x", source={"kind": "interview", "ref": "r"}, **kw)


def req(n=1, parent="N-001", ver=1, **kw):
    return item("R", n, statement="s", rationale="r", kind="system", derives_from=[{"id": parent, "ver": ver}], **kw)


def ver(n=1, target="R-001", tver=1, **kw):
    kw.setdefault("status", "planned")
    return item("V", n, method="test", verifies=[{"id": target, "ver": tver}], **kw)


def risk(n=1, control="R-001", cver=1, **kw):
    kw.setdefault("status", "open")
    return item("H", n, hazard="h", harm="m", controls=[{"id": control, "ver": cver}], **kw)


class Repo:
    """A throwaway repository root holding the four trace files."""

    def __init__(self, needs=None, reqs=None, risks=None, vers=None, board=None):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "trace").mkdir()
        (self.dir / "board.yml").write_text(yaml.safe_dump(board or {"allowed_classifications": ["public"]}))
        for name, data in (("needs", needs), ("requirements", reqs), ("risks", risks), ("verification", vers)):
            (self.dir / "trace" / f"{name}.yml").write_text(yaml.safe_dump(data or []))

    def codes(self) -> list[str]:
        _, findings = kb_check.run(self.dir)
        return [f.code for f in findings if f.level == "error"]

    def close(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


class KbCheckTest(unittest.TestCase):
    def check(self, expected: list[str], **kw) -> None:
        repo = Repo(**kw)
        self.addCleanup(repo.close)
        self.assertEqual(sorted(expected), sorted(repo.codes()))

    def test_good_chain_passes(self):
        self.check([], needs=[need()], reqs=[req(status="approved")], vers=[ver(status="planned")],
                   risks=[risk(status="controlled")])

    def test_shipped_template_passes(self):
        self.assertEqual(0, kb_check.main(["--root", str(ROOT)]))

    def test_suspect_link_when_parent_version_moves(self):
        self.check(["K008"], needs=[need(version=2)], reqs=[req()])

    def test_link_to_future_version(self):
        self.check(["K008"], needs=[need()], reqs=[req(ver=3)])

    def test_link_to_missing_item(self):
        self.check(["K007"], needs=[need()], reqs=[req(parent="N-009")])

    def test_link_to_wrong_type(self):
        self.check(["K007"], needs=[need()], reqs=[req()], vers=[ver(target="N-001")])

    def test_link_without_version(self):
        r = req()
        r["derives_from"] = [{"id": "N-001"}]
        self.check(["K007"], needs=[need()], reqs=[r])

    def test_link_to_rejected_parent(self):
        self.check(["K013"], needs=[need(status="rejected")], reqs=[req()])

    def test_approved_requirement_needs_verification_or_waiver(self):
        self.check(["K010"], needs=[need()], reqs=[req(status="approved")])
        self.check([], needs=[need()], reqs=[req(status="approved", verification_waiver="inspected at design review")])

    def test_passed_verification_needs_evidence(self):
        self.check(["K011"], needs=[need()], reqs=[req()], vers=[ver(status="passed")])
        self.check([], needs=[need()], reqs=[req()], vers=[ver(status="passed", evidence=["verification/r1.md"])])

    def test_waived_verification_needs_reason(self):
        self.check(["K011"], needs=[need()], reqs=[req()], vers=[ver(status="waived")])

    def test_duplicate_id(self):
        self.check(["K002"], needs=[need(), need()])

    def test_wrong_id_prefix_for_file(self):
        self.check(["K003"], needs=[item("R", 1, statement="s", stakeholder="x",
                                         source={"kind": "a", "ref": "b"})])

    def test_missing_required_field(self):
        n = need()
        del n["statement"]
        self.check(["K004"], needs=[n])

    def test_empty_parent_list_is_an_error(self):
        r = req()
        r["derives_from"] = []
        self.check(["K004"], needs=[need()], reqs=[r])

    def test_bad_enum_value(self):
        self.check(["K005"], needs=[need(status="maybe")])

    def test_restricted_content_rejected_in_open_board(self):
        self.check(["K006"], needs=[need(classification="restricted")])

    def test_unknown_classification(self):
        self.check(["K005"], needs=[need(classification="secret")])

    def test_controlled_risk_needs_control(self):
        r = risk(status="controlled")
        r["controls"] = []
        self.check(["K004", "K012"], needs=[need()], reqs=[req()], risks=[r])

    def test_bad_version(self):
        self.check(["K015"], needs=[need(version=0)])

    def test_missing_trace_file(self):
        repo = Repo(needs=[need()])
        self.addCleanup(repo.close)
        (repo.dir / "trace" / "risks.yml").unlink()
        self.assertEqual(["K001"], repo.codes())

    def test_invalid_yaml(self):
        repo = Repo(needs=[need()])
        self.addCleanup(repo.close)
        (repo.dir / "trace" / "needs.yml").write_text("- id: [unclosed\n")
        self.assertIn("K001", repo.codes())

    def test_coverage_counts(self):
        repo = Repo(needs=[need()], reqs=[req(1), req(2)], vers=[ver(target="R-001", status="passed", evidence=["e"])])
        self.addCleanup(repo.close)
        items, _ = kb_check.run(repo.dir)
        counts = kb_check.coverage(items)["counts"]
        self.assertEqual(1, counts["verified"])
        self.assertEqual(1, counts["unverified"])

    def test_report_is_written(self):
        repo = Repo(needs=[need()], reqs=[req()])
        self.addCleanup(repo.close)
        out = repo.dir / "out"
        self.assertEqual(0, kb_check.main(["--root", str(repo.dir), "--report", str(out)]))
        self.assertTrue((out / "trace-report.json").is_file())
        self.assertIn("| R-001 |", (out / "trace-report.md").read_text())


if __name__ == "__main__":
    unittest.main()
