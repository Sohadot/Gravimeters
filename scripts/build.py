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



def structured_graph(key: str, route: str, title: str, description: str) -> str:
    """Truthful, shared Schema.org nodes; no fabricated organization, reviews or DOI."""
    canonical = CANONICAL + route
    website_id = CANONICAL + '/#website'
    graph = [
        {'@type': 'WebSite', '@id': website_id, 'url': CANONICAL + '/',
         'name': 'Gravimeters', 'description': 'Independent source-linked gravimeter and gravity research atlas',
         'inLanguage': 'en'},
        {'@type': 'CollectionPage' if key in ('instruments', 'evidence') else 'WebPage',
         '@id': canonical + '#webpage', 'url': canonical, 'name': title,
         'description': description, 'inLanguage': 'en',
         'isPartOf': {'@id': website_id}},
    ]
    if route != '/':
        breadcrumb_id = canonical + '#breadcrumb'
        graph[1]['breadcrumb'] = {'@id': breadcrumb_id}
        graph.append({
            '@type': 'BreadcrumbList', '@id': breadcrumb_id,
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Gravimeters', 'item': CANONICAL + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': title.split(' | ')[0], 'item': canonical},
            ],
        })
    if key == 'evidence':
        # This describes the actual public curated metadata export, NOT a primary dataset
        # or independent equipment testing. Dataset schema targets Dataset Search only.
        graph.append({
            '@type': 'Dataset', '@id': canonical + '#editorial-dataset',
            'name': 'Gravimeters.com source-linked instrument and evidence index',
            'description': ('Editorial metadata on seven gravimeters, four published research records and '
                            'four application domains, with original-source links and evidence limitations. '
                            'Not independent calibration, certification or peer review.'),
            'url': canonical, 'version': '0.3.0', 'inLanguage': 'en',
            'isAccessibleForFree': True,
            'distribution': {
                '@type': 'DataDownload', 'encodingFormat': 'application/json',
                'contentUrl': CANONICAL + '/data/atlas.json',
            },
        })
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('<', '\\u003c')

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
    seo_manifest = json.loads((ROOT / 'data' / 'seo_manifest.json').read_text(encoding='utf-8'))
    records = seo_manifest.get('pages')
    if not isinstance(records, list) or not records:
        raise ValueError('SEO manifest must declare nonempty pages')
    pages = {}
    canonical_routes = set()
    for item in records:
        if not isinstance(item, dict) or set(item) != {'id', 'route', 'title', 'description', 'social_image', 'indexable'}:
            raise ValueError('SEO page must contain exactly the approved metadata fields')
        key, route = item['id'], item['route']
        if key not in {'home', 'instruments', 'navigation', 'evidence', 'acquisition'}:
            raise ValueError(f'Unapproved route identity: {key}')
        if (not isinstance(route, str) or not route.startswith('/') or
                not route.endswith('/') or '//' in route or '?' in route or '#' in route or
                route != ('/' if key == 'home' else f'/{key}/')):
            raise ValueError(f'Unapproved canonical route: {route}')
        if key in pages or route in canonical_routes:
            raise ValueError(f'Duplicate SEO page identity or route: {key} {route}')
        if not isinstance(item['indexable'], bool):
            raise ValueError(f'Indexability must be an explicit boolean for {key}')
        for field in ('title', 'description', 'social_image'):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError(f'Empty SEO metadata {field} on {key}')
        if not 24 <= len(item['title']) <= 85 or not 70 <= len(item['description']) <= 200:
            raise ValueError(f'Unexpected SEO title/description length on {key}')
        if not item['social_image'].startswith('og-') or not item['social_image'].endswith('.jpg'):
            raise ValueError(f'Invalid social image reference on {key}')
        pages[key] = (route, item['title'], item['description'], item['social_image'], item['indexable'])
        canonical_routes.add(route)
    if set(pages) != {'home', 'instruments', 'navigation', 'evidence', 'acquisition'}:
        raise ValueError('Initial release routes must remain complete; new routes require a review')
    # A clean output prevents stale routes or social assets from being deployed.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(exist_ok=True)
    for key, (route, title, description, social_image, indexable) in pages.items():
        dest = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(template.render(page=key, route=route, title=title, description=description,
                                        canonical=CANONICAL + route, social_image=CANONICAL + '/assets/' + social_image,
                                        robots_directive=('index,follow,max-image-preview:large' if indexable else 'noindex,follow'),
                                        structured_data=structured_graph(key, route, title, description),
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
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{CANONICAL}{route}</loc></url>' for route, _, _, _, indexable in pages.values() if indexable) + '</urlset>\n', encoding='utf-8')
    print(f'Built {len(pages)} routes; {len(instruments)} instruments; {len(evidence)} evidence records.')


if __name__ == '__main__':
    build()
