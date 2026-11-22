#!/usr/bin/env python3
"""Build a static, source-linked Gravimeters.com site. No deployment side effects."""
from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
CANONICAL = 'https://gravimeters.com'


def load_records(name: str, required: set[str]) -> list[dict]:
    records = json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))
    if not isinstance(records, list) or not records:
        raise ValueError(f'{name}: expected a nonempty list')
    ids = set()
    for item in records:
        if not isinstance(item, dict) or not required.issubset(item):
            raise ValueError(f'{name}: missing required fields')
        if not all(isinstance(item[field], str) and item[field].strip() for field in required):
            raise ValueError(f'{name}: empty required value')
        if item['id'] in ids:
            raise ValueError(f'{name}: duplicate id: {item["id"]}')
        ids.add(item['id'])
        if urlparse(item['source_url']).scheme != 'https':
            raise ValueError(f'{name}: source must be HTTPS')
        date.fromisoformat(item['reviewed_at'])
    return records


def build() -> None:
    instruments = load_records('instruments.json', {'id', 'model', 'manufacturer', 'measurement', 'principle', 'description', 'source_url', 'reviewed_at'})
    evidence = load_records('evidence.json', {'id', 'title', 'source_type', 'source_url', 'claim', 'boundary', 'reviewed_at'})
    applications = json.loads((ROOT / 'data' / 'applications.json').read_text(encoding='utf-8'))
    taxonomy = json.loads((ROOT / 'data' / 'taxonomy.json').read_text(encoding='utf-8'))
    schema = json.loads((ROOT / 'data' / 'schema' / 'instrument.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for item in instruments:
        violations = list(validator.iter_errors(item))
        if violations:
            raise ValueError(f'instrument {item["id"]}: {violations[0].message}')
        if item['measurement_type'] not in taxonomy['facets']['measurement_type']:
            raise ValueError(f'unknown measurement type: {item["id"]}')
        if item['sensing_family'] not in taxonomy['facets']['sensing_family']:
            raise ValueError(f'unknown sensing family: {item["id"]}')
        if item['measurement'].lower() != item['measurement_type']:
            raise ValueError(f'inconsistent measurement classification: {item["id"]}')
    # Public links are owner-editable, but must not fabricate a future DOI.
    links = json.loads((ROOT / 'data' / 'links.json').read_text(encoding='utf-8'))
    if links.get('github_repository_url') != 'https://github.com/Sohadot/Gravimeters':
        raise ValueError('Unexpected GitHub source location')
    doi_url = links.get('zenodo_record_url')
    if doi_url is not None and not (isinstance(doi_url, str) and
                                    (doi_url.startswith('https://zenodo.org/records/') or
                                     doi_url.startswith('https://doi.org/10.5281/zenodo.'))):
        raise ValueError('Zenodo link must be null until a published verified record exists')
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html']))
    template = env.get_template('site.html')
    pages = {
        'home': ('/', 'Satellite signals can be jammed. Gravity can’t. | Gravimeters', 'An independent atlas of gravity measurement instruments and primary-source evidence; explore the limits of gravity-aided navigation.', 'og-home.jpg'),
        'instruments': ('/instruments/', 'Gravity instrument atlas | Gravimeters', 'Source-linked examples across relative, absolute and quantum gravimetry.', 'og-instruments.jpg'),
        'navigation': ('/navigation/', 'Gravity-aided navigation evidence | Gravimeters', 'Source-level evidence about GNSS-independent gravity-assisted navigation, including its limitations.', 'og-navigation.jpg'),
        'evidence': ('/evidence/', 'Evidence intelligence | Gravimeters', 'Trace the scientific studies, instrument-model citations, sensing families and application boundaries behind gravity measurement.', 'og-navigation.jpg'),
        'acquisition': ('/acquisition/', 'Strategic acquisition and verifiable transfer | Gravimeters', 'Explore an independently maintained gravity-instrument reference asset and a transparent, optional third-party escrow transaction process.', 'og-acquisition.jpg'),
    }
    # A clean output prevents stale routes or social assets from being deployed.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(exist_ok=True)
    for key, (route, title, description, social_image) in pages.items():
        dest = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(template.render(page=key, route=route, title=title, description=description,
                                        canonical=CANONICAL + route, social_image=CANONICAL + '/assets/' + social_image,
                                        links=links, instruments=instruments, evidence=evidence, applications=applications,
                                        contact='agent@sohadot.com', year=date.today().year), encoding='utf-8')
    for path in (ROOT / 'static').rglob('*'):
        if path.is_file():
            target = OUT / path.relative_to(ROOT / 'static')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    # Public editorial metadata: no third-party source is re-licensed by this export.
    public_data = OUT / 'data'
    public_data.mkdir(exist_ok=True)
    (public_data / 'schema').mkdir(exist_ok=True)
    (public_data / 'schema' / 'instrument.schema.json').write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    atlas = {
        'dataset_version': '0.3.0',
        'dataset_type': 'source_linked_editorial_index',
        'publisher': 'Gravimeters.com',
        'source_repository': 'https://github.com/Sohadot/Gravimeters',
        'methodology': 'https://github.com/Sohadot/Gravimeters/blob/main/docs/CLASSIFICATION_AND_PROVENANCE.md',
        'rights_notice': 'Original editorial summaries and source pointers only. Linked third-party sources retain their own rights; no blanket third-party reuse license is implied.',
        'scope_note': 'Source summaries, not instrument certification, independent calibration, procurement advice, GNSS replacement or peer review.',
        'taxonomy': taxonomy,
        'instruments': instruments,
        'navigation_evidence': evidence,
        'applications': applications,
        'evidence_relationships_note': 'An explicit linked_instruments entry means the paper names that instrument model. A sensing_families link is only a family-level association and never a model-level endorsement.',
    }
    (public_data / 'atlas.json').write_text(
        json.dumps(atlas, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{CANONICAL}{route}</loc></url>' for route, _, _, _ in pages.values()) + '</urlset>\n', encoding='utf-8')
    print(f'Built {len(pages)} routes; {len(instruments)} instruments; {len(evidence)} evidence records.')


if __name__ == '__main__':
    build()
