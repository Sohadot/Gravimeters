"""Deterministic tests for bounded, non-destructive reference observations."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reference_integrity import audit, classify, collect_references, identity_signal, safe_https_url


class ReferenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()
        self.write('instruments.json', [{
            'id': 'model-one', 'model': 'Model One', 'source_url': 'https://maker.example.edu/model',
            'reviewed_at': '2026-11-20'
        }])
        self.write('evidence.json', [{
            'id': 'paper-one', 'source_title': 'Gravity Research Paper',
            'source_url': 'https://papers.example.edu/paper',
            'source_doi': '10.1234/grav.2024.abc', 'reviewed_at': '2026-11-20'
        }])

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        (self.root / 'data' / name).write_text(json.dumps(data), encoding='utf-8')

    def test_https_source_guard(self):
        self.assertTrue(safe_https_url('https://arxiv.org/abs/2608.25563'))
        for url in ('http://arxiv.org/abs/1', 'https://127.0.0.1/secret',
                    'https://localhost/', 'https://example.org/',
                    'https://user:pass@nature.com/a', 'https://site.local/a',
                    'https://nature.com/a#local', 'https://nature.com:8443/a'):
            with self.subTest(url=url):
                self.assertFalse(safe_https_url(url))

    def test_manifest_has_source_and_publication_doi_separately(self):
        sources = collect_references(self.root)
        self.assertEqual(len(sources), 3)
        self.assertEqual({x['source_kind'] for x in sources},
                         {'instrument_source', 'research_source', 'original_publication_doi'})

    def test_manifest_rejects_bad_source(self):
        self.write('instruments.json', [{'id':'x', 'model':'M', 'source_url':'http://localhost/', 'reviewed_at':'2026-01-01'}])
        with self.assertRaises(ValueError):
            collect_references(self.root)

    def test_manifest_rejects_bad_doi(self):
        self.write('evidence.json', [{'id':'x','source_title':'X', 'source_url':'https://arxiv.org/abs/1','source_doi':'invalid', 'reviewed_at':'2026-01-01'}])
        with self.assertRaises(ValueError):
            collect_references(self.root)

    def test_healthy_response_is_observation_not_scientific_verification(self):
        row = collect_references(self.root)[0]
        out = classify(row, lambda url: {
            'http_status':200, 'resolved_url':url, 'title_observed':row['title_hint'],
            'sample_sha256':'ab'*32, 'sample_truncated': False
        })
        self.assertEqual(out['observation'], 'reachable')
        self.assertEqual(out['title_signal'], 'consistent')
        self.assertNotIn('scientifically_verified', out)

    def test_404_is_observed_not_found_without_deleting_source(self):
        row = collect_references(self.root)[0]
        def missing(_):
            raise HTTPError(row['url'], 404, 'not found', {}, None)
        result = classify(row, missing)
        self.assertEqual(result['observation'], 'observed_not_found')
        self.assertEqual(result['record_ids'], row['record_ids'])

    def test_403_is_access_limited(self):
        row = collect_references(self.root)[0]
        def forbidden(_):
            raise HTTPError(row['url'], 403, 'forbidden', {}, None)
        self.assertEqual(classify(row, forbidden)['observation'], 'access_limited')

    def test_network_failure_stays_unverified(self):
        row = collect_references(self.root)[0]
        self.assertEqual(classify(row, lambda _: (_ for _ in ()).throw(URLError('timeout')))['observation'], 'network_unverified')

    def test_mismatched_title_requests_review_not_rejection(self):
        row = collect_references(self.root)[0]
        res = classify(row, lambda url: {'http_status': 200, 'resolved_url': url, 'title_observed': 'Unrelated Resource'})
        self.assertEqual(res['observation'], 'reachable')
        self.assertEqual(res['title_signal'], 'review_title')
        self.assertEqual(identity_signal('Gravity Research Paper', 'Gravity Research Paper | Publisher'), 'consistent')

    def test_offline_report_never_probes_network(self):
        report = audit(self.root, online=False, fetcher=lambda _: self.fail('Network called during offline audit'))
        self.assertEqual(report['status_counts'], {'not_checked':3})
        self.assertIn('not proof of scientific accuracy', report['method_limits'])

    def test_online_report_preserves_all_references_after_failure(self):
        def fail(_):
            raise URLError('network')
        report = audit(self.root, online=True, fetcher=fail)
        self.assertEqual(len(report['references']), 3)
        self.assertEqual(report['status_counts']['network_unverified'], 3)


if __name__ == '__main__':
    unittest.main()
