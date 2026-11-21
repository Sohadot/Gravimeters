#!/usr/bin/env python3
"""Launch-critical offline checks, intentionally scoped to PR #1."""
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
for route in ('/', '/instruments/', '/navigation/', '/acquisition/'):
    path = OUT / route.strip('/') / 'index.html' if route != '/' else OUT / 'index.html'
    assert path.exists(), f'missing page {route}'
    html = path.read_text(encoding='utf-8')
    parser = PageParser()
    parser.feed(html)
    assert parser.h1 == 1, (route, parser.h1)
    assert '<title>' in html and 'rel="canonical"' in html
    assert 'og:image:width' in html and 'og:image:height' in html
    assert 'twitter:card' in html and 'twitter:image' in html
    assert f'https://gravimeters.com/assets/og-{route.strip("/") or "home"}.jpg' in html
    assert 'placeholder-doi' not in html and '10.5281/zenodo.0000000' not in html
    assert 'Internal Master' not in html and 'BUYER_PIPELINE' not in html
    for href in parser.links:
        if href.startswith('/') and not href.startswith('//') and not href.startswith('/#'):
            bare = href.split('#')[0].split('?')[0]
            assert (OUT / bare.lstrip('/') / 'index.html').exists() or (OUT / bare.lstrip('/')).is_file(), (route, href)
assert (OUT / 'robots.txt').is_file()
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
print('PR #1 smoke test passed (local static output only).')
