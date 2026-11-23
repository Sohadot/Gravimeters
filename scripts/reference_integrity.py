#!/usr/bin/env python3
"""Bounded, read-only external reference audit for Gravimeters.com.

The report offers observational signals, not proof of scientific validity,
retraction status or current metrological suitability. No writes to sources.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = 'GravimetersReferenceAudit/1.0 (+https://gravimeters.com/; read-only)' 
MAX_BYTES = 256 * 1024
TIMEOUT_SECONDS = 12
TOKEN_PATTERN = re.compile(r'[a-z0-9]+', re.IGNORECASE)
STOPWORDS = {'the', 'and', 'with', 'for', 'from', 'of', 'in', 'to', 'an', 'a', 'as', 'on', 'by', 'at', 'is', 'new', 'using', 'based'}


class UnsafeReference(ValueError):
    """A URL is not suitable for outbound source probing."""


def safe_https_url(value: str) -> bool:
    if not isinstance(value, str) or len(value) > 2048:
        return False
    try:
        url = urlsplit(value)
        host = url.hostname or ''
        if url.scheme != 'https' or not host or url.username or url.password or url.fragment:
            return False
        if url.port not in (None, 443):
            return False
        if host in {'localhost', 'example.com', 'example.org', 'example.net'} or host.endswith(('.local', '.internal')):
            return False
        try:
            ipaddress.ip_address(host)
            return False
        except ValueError:
            return '.' in host and all(part for part in host.split('.'))
    except ValueError:
        return False


class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not safe_https_url(newurl):
            raise UnsafeReference('Redirect target is not a trusted public HTTPS URL')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class TitleReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)

    @property
    def title(self) -> str:
        return ' '.join(html.unescape(''.join(self.parts)).split())[:300]


def identity_signal(expected: str, found: str) -> str:
    """Conservative title-matching hint; weak titles remain 'review', never 'invalid'."""
    if not found:
        return 'not_observed'
    expected_tokens = {t for t in TOKEN_PATTERN.findall(expected.lower()) if t not in STOPWORDS and len(t) > 2}
    found_tokens = set(TOKEN_PATTERN.findall(found.lower()))
    if not expected_tokens:
        return 'not_assessed'
    shared = expected_tokens & found_tokens
    # Manufacturer pages sometimes use a shorter product title; one rare token is informative.
    return 'consistent' if len(shared) >= max(1, (len(expected_tokens) + 1) // 2) else 'review_title'


def collect_references(root: Path) -> list[dict]:
    """Derive a deterministic, deduplicated manifest from published editorial sources."""
    data = root / 'data'
    instruments = json.loads((data / 'instruments.json').read_text(encoding='utf-8'))
    evidence = json.loads((data / 'evidence.json').read_text(encoding='utf-8'))
    registry: dict[str, dict] = {}

    def add(kind: str, item_id: str, url: str, title: str, reviewed_at: str):
        if not safe_https_url(url):
            raise UnsafeReference(f'{kind}:{item_id} has unsafe reference URL')
        record = registry.setdefault(url, {
            'url': url, 'source_kind': kind, 'title_hint': title,
            'editorial_reviewed_at': reviewed_at, 'record_ids': []
        })
        record['record_ids'].append(item_id)

    seen_ids = set()
    for item in instruments:
        key = 'instrument:' + item['id']
        if key in seen_ids:
            raise ValueError('Duplicate instrument identifier: ' + key)
        seen_ids.add(key)
        add('instrument_source', key, item['source_url'], item['model'], item['reviewed_at'])
    for item in evidence:
        key = 'evidence:' + item['id']
        if key in seen_ids:
            raise ValueError('Duplicate evidence identifier: ' + key)
        seen_ids.add(key)
        add('research_source', key, item['source_url'], item['source_title'], item['reviewed_at'])
        if item.get('source_doi'):
            doi = item['source_doi']
            if not re.fullmatch(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', doi):
                raise ValueError(f'{key} contains malformed DOI')
            add('original_publication_doi', key, 'https://doi.org/' + doi, item['source_title'], item['reviewed_at'])
    return [registry[url] for url in sorted(registry)]


def fetch_reference(url: str) -> dict:
    """Make a bounded GET, checking redirects and recording only a title and body digest."""
    if not safe_https_url(url):
        raise UnsafeReference('Unsafe reference URL')
    opener = build_opener(SafeRedirects())
    request = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.5'})
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        target = response.geturl()
        if not safe_https_url(target):
            raise UnsafeReference('Non-HTTPS or unsafe final URL')
        body = response.read(MAX_BYTES + 1)
        limited = len(body) > MAX_BYTES
        sample = body[:MAX_BYTES]
        encoding = response.headers.get_content_charset() or 'utf-8'
        document = sample.decode(encoding, errors='replace')
        title = TitleReader()
        title.feed(document)
        return {
            'http_status': response.getcode(), 'resolved_url': target,
            'title_observed': title.title, 'sample_sha256': hashlib.sha256(sample).hexdigest(),
            'sample_truncated': limited
        }


def classify(row: dict, fetcher=fetch_reference) -> dict:
    result = {
        'url': row['url'], 'source_kind': row['source_kind'], 'record_ids': row['record_ids'],
        'title_hint': row['title_hint'], 'editorial_reviewed_at': row['editorial_reviewed_at'],
        'observation': 'not_checked', 'title_signal': 'not_observed', 'http_status': None,
        'resolved_url': None, 'title_observed': None, 'sample_sha256': None,
        'sample_truncated': None,
    }
    try:
        observed = fetcher(row['url'])
        result.update(observed)
        status = observed.get('http_status')
        result['observation'] = 'reachable' if status and 200 <= status < 300 else 'http_unexpected'
        result['title_signal'] = identity_signal(row['title_hint'], observed.get('title_observed') or '')
        if observed.get('resolved_url') and observed['resolved_url'] != row['url']:
            result['redirect_observed'] = True
    except UnsafeReference:
        result['observation'] = 'unsafe_redirect_or_url'
    except HTTPError as exc:
        result['http_status'] = exc.code
        result['observation'] = ('access_limited' if exc.code in (401, 403) else
                                 'rate_limited' if exc.code == 429 else
                                 'observed_not_found' if exc.code in (404, 410) else
                                 'upstream_error' if exc.code >= 500 else 'http_unexpected')
    except (URLError, TimeoutError, ConnectionError, OSError, UnicodeError, LookupError):
        result['observation'] = 'network_unverified'
    return result


def audit(root: Path, online: bool = False, fetcher=fetch_reference) -> dict:
    sources = collect_references(root)
    checked_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    if online:
        results = [classify(row, fetcher) for row in sources]
    else:
        results = [{**row, 'observation': 'not_checked'} for row in sources]
    statuses: dict[str, int] = {}
    for item in results:
        statuses[item['observation']] = statuses.get(item['observation'], 0) + 1
    return {
        'report_schema_version': '1.0', 'generated_at_utc': checked_at,
        'mode': 'online_read_only' if online else 'offline_manifest',
        'project': 'Gravimeters.com', 'source_count': len(sources),
        'status_counts': statuses,
        'method_limits': (
            'External HTTP and page-title observations only. HTTP 200 is not proof of scientific accuracy, '
            'source validity, absence of retraction, or continued suitability. Access restrictions, '
            'transient network failures and title differences require human review; no automatic record deletion.'
        ),
        'references': results
    }


def summary_markdown(report: dict) -> str:
    lines = [
        '## Gravimeters — Reference Integrity Audit',
        '', f"Mode: **{report['mode']}** | UTC: {report['generated_at_utc']}",
        f"References: **{report['source_count']}**", '',
        '| Observation | Count |', '| --- | ---: |',
    ]
    lines += [f'| {key} | {value} |' for key, value in sorted(report['status_counts'].items())]
    lines += ['', '| Reference | Observation | HTTP | Title signal |', '| --- | --- | --- | --- |']
    for item in report['references']:
        u = item['url']
        lines.append(f"| {u} | {item['observation']} | {item.get('http_status') or '—'} | {item.get('title_signal', '—')} |")
    lines += ['', '**Limit:** ' + report['method_limits'], '']
    return '\n'.join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--online', action='store_true', help='Check external URLs; never modify sources or site')
    p.add_argument('--output', type=Path, help='Write JSON report to a local CI artifact path')
    args = p.parse_args(argv)
    try:
        report = audit(ROOT, online=args.online)
    except (ValueError, KeyError, json.JSONDecodeError, OSError, UnsafeReference) as exc:
        print('REFERENCE MANIFEST FAILED: ' + str(exc), file=sys.stderr)
        return 1
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    else:
        print(payload)
    print('Reference manifest: %d distinct sources (%s)' % (report['source_count'], report['mode']))
    summary_path = __import__('os').environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8') as out:
            out.write(summary_markdown(report))
    # External failures are observational only; canonical data/schema failure blocks.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
