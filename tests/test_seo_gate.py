"""Negative tests: SEO audit must fail closed if key search signals drift."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import OUT, build
from seo_gate import audit


class SeoGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.dist = Path(self.directory.name) / "dist"
        shutil.copytree(OUT, self.dist)
        self.manifest = ROOT / "data" / "seo_manifest.json"

    def replace(self, name, old, new):
        path = self.dist / name
        body = path.read_text(encoding="utf-8")
        self.assertIn(old, body)
        path.write_text(body.replace(old, new, 1), encoding="utf-8")

    def test_baseline_passes(self):
        self.assertEqual(audit(self.dist, self.manifest), [])

    def test_duplicate_or_wrong_canonical_fails(self):
        self.replace("evidence/index.html", 'rel="canonical" href="https://gravimeters.com/evidence/"',
                     'rel="canonical" href="https://gravimeters.com/"')
        self.assertTrue(audit(self.dist, self.manifest))

    def test_noindex_not_in_sitemap_fails(self):
        self.replace("navigation/index.html", 'name="robots" content="index,follow,max-image-preview:large"',
                     'name="robots" content="noindex,follow"')
        self.assertTrue(audit(self.dist, self.manifest))

    def test_bad_sitemap_fails(self):
        self.replace("sitemap.xml", "<loc>https://gravimeters.com/evidence/</loc>",
                     "<loc>https://gravimeters.com/unapproved/</loc>")
        self.assertTrue(audit(self.dist, self.manifest))

    def test_missing_dataset_distribution_fails(self):
        self.replace("evidence/index.html", "https://gravimeters.com/data/atlas.json",
                     "https://gravimeters.com/data/nonexistent.json")
        self.assertTrue(audit(self.dist, self.manifest))

    def test_robots_blocking_fails(self):
        self.replace("robots.txt", "Allow: /", "Disallow: /")
        self.assertTrue(audit(self.dist, self.manifest))

    def test_missing_open_graph_image_fails(self):
        (self.dist / "assets" / "og-home.jpg").unlink()
        self.assertTrue(audit(self.dist, self.manifest))

    def test_broken_json_ld_fails(self):
        self.replace("index.html", '"@context": "https://schema.org"',
                     '"@context": "https://example.org"')
        self.assertTrue(audit(self.dist, self.manifest))


if __name__ == "__main__":
    unittest.main()
