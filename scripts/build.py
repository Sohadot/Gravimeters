#!/usr/bin/env python3
"""Build a static, source-linked Gravimeters.com site. No deployment side effects."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

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
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html']))
    template = env.get_template('site.html')
    pages = {
        'home': ('/', 'Satellite signals can be jammed. Gravity can’t. | Gravimeters', 'An independent atlas of gravity measurement instruments and primary-source evidence; explore the limits of gravity-aided navigation.'),
        'instruments': ('/instruments/', 'Gravity instrument atlas | Gravimeters', 'Source-linked examples across relative, absolute and quantum gravimetry.'),
        'navigation': ('/navigation/', 'Gravity-aided navigation evidence | Gravimeters', 'Source-level evidence about GNSS-independent gravity-assisted navigation, including its limitations.'),
    }
    OUT.mkdir(exist_ok=True)
    for key, (route, title, description) in pages.items():
        dest = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(template.render(page=key, route=route, title=title, description=description,
                                        canonical=CANONICAL + route, instruments=instruments, evidence=evidence,
                                        contact='agent@sohadot.com', year=date.today().year), encoding='utf-8')
    for path in (ROOT / 'static').rglob('*'):
        if path.is_file():
            target = OUT / path.relative_to(ROOT / 'static')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{CANONICAL}{route}</loc></url>' for route, _, _ in pages.values()) + '</urlset>\n', encoding='utf-8')
    print(f'Built {len(pages)} routes; {len(instruments)} instruments; {len(evidence)} evidence records.')


if __name__ == '__main__':
    build()
