"""Tests prove governance gates reject representative broken/insecure changes."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from governance_gate import audit_data, audit_files, audit_repository, audit_workflows, audit_source_paths  # noqa: E402


class GovernanceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("data", ".github/workflows", "scripts"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        for path in (
            "data/instruments.json", "data/evidence.json", "data/taxonomy.json",
            "data/schema/instrument.schema.json", "data/links.json",
            ".github/workflows/check.yml", ".github/workflows/deploy-pages.yml",
            "scripts/build.py",
        ):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        # Prior smoke_test step builds ROOT/dist; tests only need to validate its contents.
        self.dist = self.root / "dist"
        shutil.copytree(ROOT / "dist", self.dist)

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, path):
        return json.loads((self.root / path).read_text(encoding="utf-8"))

    def write(self, path, data):
        (self.root / path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def test_baseline_passes(self):
        self.assertEqual(audit_repository(self.root), [])

    def test_rejects_contradictory_instrument_taxonomy(self):
        data = self.load("data/instruments.json")
        data[0]["measurement_type"] = "absolute"
        self.write("data/instruments.json", data)
        self.assertTrue(any("contradictory" in s for s in audit_data(self.root)))

    def test_rejects_untrusted_source(self):
        data = self.load("data/instruments.json")
        data[0]["source_url"] = "https://localhost/secret"
        self.write("data/instruments.json", data)
        self.assertTrue(any("source URL" in s for s in audit_data(self.root)))

    def test_rejects_future_review_date(self):
        data = self.load("data/instruments.json")
        data[0]["reviewed_at"] = "2099-01-01"
        self.write("data/instruments.json", data)
        self.assertTrue(any("future review date" in s for s in audit_data(self.root)))

    def test_rejects_pretend_doi(self):
        data = self.load("data/links.json")
        data["zenodo_record_url"] = "https://doi.org/10.5281/zenodo.12345"
        self.write("data/links.json", data)
        self.assertTrue(any("DOI" in s for s in audit_data(self.root)))

    def test_rejects_direct_auto_publication(self):
        path = self.root / ".github/workflows/deploy-pages.yml"
        txt = path.read_text(encoding="utf-8").replace("  workflow_dispatch:", "  push:")
        path.write_text(txt, encoding="utf-8")
        self.assertTrue(any("exclusively manual" in s for s in audit_workflows(self.root)))

    def test_rejects_unpinned_action(self):
        path = self.root / ".github/workflows/check.yml"
        txt = path.read_text(encoding="utf-8").replace("uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262", "uses: actions/checkout@v4")
        path.write_text(txt, encoding="utf-8")
        self.assertTrue(any("immutable full SHA" in s for s in audit_workflows(self.root)))

    def test_rejects_private_file_in_public_repo(self):
        (self.root / "GRAVIMETERS_DECISIONS_LOG.md").write_text("not public", encoding="utf-8")
        self.assertTrue(any("filename" in s for s in audit_source_paths(self.root)))

    def test_rejects_credential_in_public_source(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/example.md").write_text("ghp_" + "A" * 40, encoding="utf-8")
        self.assertTrue(any("credential" in s for s in audit_source_paths(self.root)))

    def test_rejects_internal_export(self):
        (self.dist / "GRAVIMETERS_DECISIONS_LOG.md").write_text("Private strategy", encoding="utf-8")
        self.assertTrue(any("Private" in s for s in audit_files(self.root)))

    def test_rejects_fake_peer_review_label(self):
        records = self.load("data/evidence.json")
        records[0]["source_type"] = "Peer-reviewed paper"
        self.write("data/evidence.json", records)
        self.assertTrue(any("preprint" in s for s in audit_data(self.root)))


if __name__ == "__main__":
    unittest.main()
