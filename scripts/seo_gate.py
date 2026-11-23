#!/usr/bin/env python3
"""Deterministic release SEO audit: canonical, indexation, sitemap, robots, JSON-LD.

No network access. No Search Console actions, redirects or publication effects.
Google chooses indexing/ranking; passing this audit is not a search ranking claim.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "data" / "seo_manifest.json"
DOMAIN = "https://gravimeters.com"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.title = []
        self.meta = {}
        self.links = []
        self.h1_count = 0
        self._capturing_title = False
        self._capturing_schema = False
        self._schema_parts = []
        self.schemas = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "html":
            self.lang = fields.get("lang")
        if tag == "title":
            self._capturing_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta":
            name = fields.get("name") or fields.get("property")
            if name:
                self.meta.setdefault(name, []).append(fields.get("content"))
        if tag == "link":
            self.links.append(fields)
        if tag == "script" and fields.get("type") == "application/ld+json":
            self._capturing_schema = True
            self._schema_parts = []

    def handle_data(self, data):
        if self._capturing_title:
            self.title.append(data)
        if self._capturing_schema:
            self._schema_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._capturing_title = False
        if tag == "script" and self._capturing_schema:
            self.schemas.append("".join(self._schema_parts))
            self._capturing_schema = False


def audit(dist: Path = DIST, manifest_path: Path = MANIFEST) -> list[str]:
    """Return every encountered violation without modifying the site."""
    errors = []
    try:
        obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        pages = obj["pages"]
        assert isinstance(pages, list) and pages
    except (OSError, ValueError, KeyError, AssertionError, TypeError) as exc:
        return [f"Invalid SEO manifest: {exc}"]
    expected_indexable = set()
    canonical_routes = set()
    titles = set()
    descriptions = set()
    for page in pages:
        try:
            route = page["route"]
            key = page["id"]
            canonical = DOMAIN + route
            assert route.startswith("/") and route.endswith("/") and "?" not in route and "#" not in route
            assert route not in canonical_routes
            canonical_routes.add(route)
            assert isinstance(page["indexable"], bool)
            if page["indexable"]:
                expected_indexable.add(canonical)
            html_path = dist / "index.html" if route == "/" else dist / route.strip("/") / "index.html"
            html = html_path.read_text(encoding="utf-8")
            parsed = HeadParser()
            parsed.feed(html)
            found_title = "".join(parsed.title).strip()
            assert parsed.lang == "en", "html language not declared"
            assert parsed.h1_count == 1, "page must have one H1"
            assert found_title == page["title"], "title mismatch"
            assert parsed.meta.get("description") == [page["description"]], "description mismatch"
            assert found_title not in titles, "duplicate title"
            assert page["description"] not in descriptions, "duplicate description"
            titles.add(found_title)
            descriptions.add(page["description"])
            canonicals = [link.get("href") for link in parsed.links if "canonical" in (link.get("rel") or "").split()]
            assert canonicals == [canonical], "canonical missing or duplicated"
            assert parsed.meta.get("robots") == [("index,follow,max-image-preview:large" if page["indexable"] else "noindex,follow")], "robots directive mismatch"
            assert parsed.meta.get("og:url") == [canonical], "Open Graph canonical mismatch"
            assert parsed.meta.get("og:image") == [DOMAIN + "/assets/" + page["social_image"]], "Open Graph image mismatch"
            assert (dist / "assets" / page["social_image"]).is_file(), "OG image file missing"
            assert len(parsed.schemas) == 1, "exactly one JSON-LD graph required"
            graph = json.loads(parsed.schemas[0])
            assert graph.get("@context") == "https://schema.org"
            nodes = graph["@graph"]
            assert isinstance(nodes, list)
            website = next(x for x in nodes if x.get("@type") == "WebSite")
            webpage = next(x for x in nodes if x.get("@type") in ("WebPage", "CollectionPage"))
            assert website["url"] == DOMAIN + "/"
            assert webpage["url"] == canonical and webpage["name"] == page["title"]
            assert webpage["description"] == page["description"]
            if route == "/":
                assert not any(x.get("@type") == "BreadcrumbList" for x in nodes)
            else:
                breadcrumb = next(x for x in nodes if x.get("@type") == "BreadcrumbList")
                assert [x["item"] for x in breadcrumb["itemListElement"]] == [DOMAIN + "/", canonical]
                assert [x["position"] for x in breadcrumb["itemListElement"]] == [1, 2]
            if key == "evidence":
                dataset = next(x for x in nodes if x.get("@type") == "Dataset")
                assert dataset["version"] == "0.3.0", "dataset schema out of sync"
                assert dataset["distribution"]["contentUrl"] == DOMAIN + "/data/atlas.json"
                assert (dist / "data" / "atlas.json").is_file()
                data = json.loads((dist / "data" / "atlas.json").read_text(encoding="utf-8"))
                assert data["dataset_version"] == dataset["version"]
            else:
                assert not any(x.get("@type") == "Dataset" for x in nodes)
        except (AssertionError, OSError, ValueError, TypeError, KeyError, StopIteration) as exc:
            errors.append(f"SEO page {page.get('route') if isinstance(page, dict) else 'unknown'}: {exc or 'invalid markup or metadata'}")
    try:
        tree = ET.fromstring((dist / "sitemap.xml").read_text(encoding="utf-8"))
        assert tree.tag == SITEMAP_NS + "urlset", "invalid XML sitemap namespace"
        urls = [loc.text for loc in tree.findall(f"{SITEMAP_NS}url/{SITEMAP_NS}loc")]
        assert len(urls) == len(set(urls)), "duplicate sitemap URLs"
        assert set(urls) == expected_indexable, "sitemap != canonical indexable routes"
        assert all(x and urlsplit(x).scheme == "https" and urlsplit(x).netloc == "gravimeters.com" for x in urls)
        assert not list(tree.iter(SITEMAP_NS + "lastmod")), "no unverified lastmod allowed"
    except (ET.ParseError, OSError, AssertionError, TypeError) as exc:
        errors.append(f"Sitemap: {exc or 'invalid sitemap'}")
    try:
        robots = (dist / "robots.txt").read_text(encoding="utf-8")
        assert re.search(r"(?mi)^User-agent:\s*\*\s*$", robots)
        assert re.search(r"(?mi)^Allow:\s*/\s*$", robots)
        assert f"Sitemap: {DOMAIN}/sitemap.xml" in robots
        assert not re.search(r"(?mi)^Disallow:\s*/\s*$", robots)
    except (AssertionError, OSError) as exc:
        errors.append(f"Robots: {exc or 'invalid robots.txt'}")
    try:
        emitted = set()
        for f in dist.rglob("index.html"):
            rel = f.relative_to(dist)
            route = "/" if len(rel.parts) == 1 else "/" + "/".join(rel.parts[:-1]) + "/"
            emitted.add(route)
        assert emitted == canonical_routes, f"emitted routes {sorted(emitted)} do not match manifest"
    except (OSError, AssertionError) as exc:
        errors.append(f"Route inventory: {exc}")
    return errors


if __name__ == "__main__":
    issues = audit()
    if issues:
        for issue in issues:
            print("SEO GATE FAILED:", issue, file=sys.stderr)
        raise SystemExit(1)
    print("SEO GATE PASSED: canonical, robots, sitemap, indexability, Schema.org and route inventory")
