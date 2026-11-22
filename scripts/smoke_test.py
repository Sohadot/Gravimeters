#!/usr/bin/env python3
"""Launch-critical static output, source-relationship and governance invariants."""
import json
from html.parser import HTMLParser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import build, OUT


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.links = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and props.get('href'):
            self.links.append(props['href'])


build()
for route in ('/', '/instruments/', '/navigation/', '/evidence/', '/acquisition/'):
    path = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
    assert path.exists(), f'missing page {route}'
    html = path.read_text(encoding='utf-8')
    parser = PageParser()
    parser.feed(html)
    assert parser.h1 == 1, (route, parser.h1)
    assert '<title>' in html and 'rel="canonical"' in html
    assert 'og:image:width' in html and 'og:image:height' in html and 'image/jpeg' in html
    assert 'twitter:card' in html and 'twitter:image' in html
    assert f'https://gravimeters.com/assets/og-{("navigation" if route == "/evidence/" else route.strip("/") or "home")}.jpg' in html
    assert 'placeholder-doi' not in html and '10.5281/zenodo.0000000' not in html
    assert 'Internal Master' not in html and 'BUYER_PIPELINE' not in html
    for href in parser.links:
        if href.startswith('/') and not href.startswith('//') and not href.startswith('/#'):
            bare = href.split('#')[0].split('?')[0]
            assert (OUT / bare.lstrip('/') / 'index.html').exists() or (OUT / bare.lstrip('/')).is_file(), (route, href)
assert (OUT / 'robots.txt').is_file()
assert (OUT / 'sitemap.xml').is_file()
sitemap = (OUT / 'sitemap.xml').read_text(encoding='utf-8')
for route in ('/', '/instruments/', '/navigation/', '/evidence/', '/acquisition/'):
    assert f'https://gravimeters.com{route}' in sitemap, (route, 'missing sitemap URL')
assert '<loc>' in sitemap
# No generated site output may contain internal strategic document names.
for page in OUT.rglob('*.html'):
    body = page.read_text(encoding='utf-8')
    assert 'GRAVIMETERS_INTERNAL_MASTER_PLAN' not in body
    assert 'file_0000000' not in body

for route in ('home','instruments','navigation','acquisition'):
    assert (OUT / 'assets' / f'og-{route}.jpg').is_file()
    with (OUT / 'assets' / f'og-{route}.jpg').open('rb') as image:
        header=image.read(3)
        assert header == b'\xff\xd8\xff'
        assert image.seek(0, 2) > 25000
acquisition=(OUT / 'acquisition' / 'index.html').read_text(encoding='utf-8')
assert 'https://github.com/Sohadot/Gravimeters' in acquisition
assert 'https://www.escrow.com/domains/how-it-works' in acquisition
assert 'About the Zenodo platform' in acquisition and 'DOI / NOT YET ISSUED' in acquisition
assert 'No active escrow account' in acquisition
assert '10.5281/zenodo.' not in acquisition

# The Pages workflow must remain owner-triggered, never an auto-deploy on commit.
deploy = (Path(__file__).resolve().parents[1] / '.github/workflows/deploy-pages.yml').read_text(encoding='utf-8')
assert 'workflow_dispatch:' in deploy and 'push:' not in deploy and 'pull_request:' not in deploy
assert "github.ref == 'refs/heads/main'" in deploy
assert 'path: dist' in deploy
atlas = json.loads((OUT / 'data' / 'atlas.json').read_text(encoding='utf-8'))
assert atlas['dataset_version'] == '0.3.0'
assert len(atlas['instruments']) == 7 and len(atlas['navigation_evidence']) == 4 and len(atlas['applications']) == 4
assert {entry['id'] for entry in atlas['instruments']} == {'cg6', 'fg5x', 'aqg', 'a10', 'gphonex', 'igrav', 'burris'}
assert {entry['measurement_type'] for entry in atlas['instruments']} == {'relative', 'absolute'}
assert all(entry['sensing_family'] in atlas['taxonomy']['facets']['sensing_family'] for entry in atlas['instruments'])
assert (OUT / 'data' / 'schema' / 'instrument.schema.json').is_file()
assert b'GRAVIMETERS_INTERNAL' not in (OUT / 'data' / 'atlas.json').read_bytes()
instrument_page = (OUT / 'instruments' / 'index.html').read_text(encoding='utf-8')
assert '/data/atlas.json' in instrument_page
print('Static site and public atlas export tests passed.')

# User-facing comparison must be source-linked, filterable and accessible as static HTML.
page = (OUT / 'instruments' / 'index.html').read_text(encoding='utf-8')
assert page.count('data-measurement=') == 14
assert 'id="atlas-filter"' in page and 'id="visible-instrument-count"' in page
assert 'role="region"' in page and '<table class="comparison-matrix"' in page
assert 'https://www.gwrinstruments.com/igrav-gravity-sensors.html' in page
assert (OUT / 'atlas-filter.js').exists()
assert 'ranking' not in page.lower() or 'not a ranking' in page.lower()
print('Sprint 4 atlas expansion/comparison checks passed.')

# Sprint 5 application/evidence relationships are public, traceable and honest.
registry = (OUT / 'evidence' / 'index.html').read_text(encoding='utf-8')
assert registry.count('data-evidence-id=') == 4
assert registry.count('class="evidence-entry"') == 4
assert 'PREPRINT · NOT PEER-REVIEWED' in registry
assert 'No specific catalog model linked.' in registry
assert 'model_explicitly_named_in_source' not in registry  # relationships are human-readable
assert 'https://doi.org/10.1038/s41598-024-57253-1' in registry
assert 'https://github.com/Sohadot/Gravimeters/blob/main/docs/EVIDENCE_RELATIONSHIP_METHOD.md' in registry
assert (OUT / 'evidence-filter.js').is_file()
assert len({a['id'] for a in atlas['applications']}) == 4
assert sum(len(r['linked_instruments']) for r in atlas['navigation_evidence']) == 2
assert all(not r['linked_instruments'] for r in atlas['navigation_evidence'] if r['evidence_status'] == 'preprint')
nav = (OUT / 'navigation' / 'index.html').read_text(encoding='utf-8')
assert 'GNSS-free gravity-aided navigation in a maritime field trial' in nav
assert 'Sicily absolute gravity and height reference network' not in nav
print('Sprint 5 typed evidence graph and public registry checks passed.')
