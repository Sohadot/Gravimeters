# Reference integrity and provenance observation — v1

This document describes a **read-only scientific/reference continuity check**, not a proof of scientific correctness, a retraction registry, third-party certification, or a claim of current author/manufacturer endorsement.

## Scope and reproducibility

- Canonical inputs: source URLs from `data/instruments.json`, `data/evidence.json`, and the **original publication DOI URLs** derived from `source_doi`. The DOI URLs belong to the articles, **not** to Gravimeters.com.
- Source records are deduplicated deterministically and linked back to their stable editorial IDs.
- The script `scripts/reference_integrity.py` produces structured JSON reports. Use `python scripts/reference_integrity.py --output reference-manifest.json` for a **network-free** manifest, or add `--online` for bounded external HTTP observations.
- `.github/workflows/reference-integrity.yml` runs on a weekly schedule or manually; it has **read-only GitHub permissions**, preserves reports as CI artifacts for **30 days**, and **never pushes a commit, changes a study record, publishes a site, or contacts a vendor**.
- The online checker uses bounded GETs, short timeouts, a descriptive user agent, a 256 KiB response sample, and HTTPS-only URL checks. Reports contain observed HTTP status, resolved URL, page title, title-identity heuristic, sample SHA-256 digest, truncation flag, timestamp and stable source IDs.
- Dynamic website rendering may change a fingerprint without changing the scientific content. Conversely, a stable title and HTTP 200 do **not** prove that article findings or institutional authority remain unchanged.

## Reading results correctly

| Observed result | Interpretation | Editorial next action |
| --- | --- | --- |
| `reachable` | An HTTP success was observed at the check time | Do **not** equate it with scientific validation |
| `review_title` | The fetched HTML title differs from the expected subject | Inspect the page manually for possible identity drift |
| `observed_not_found` | A 404/410 response was seen | Recheck before labeling the reference unavailable |
| `access_limited` | 401/403, possibly a bot protection or paywall | Verify in a browser; do not delete the reference |
| `rate_limited` | 429 from the provider | Avoid repeated requests; defer verification |
| `network_unverified` | Timeout, TLS or transport error | Retry later, without turning it into an invalidation claim |
| `unsafe_redirect_or_url` | Redirect/URL failed the outbound HTTPS safety rule | Human security review required |

**Governance boundary:** This external audit is an observation lane, **not** the mandatory PR `check`. The existing fail-closed offline quality, source provenance, privacy and release gates remain the mandatory merge and manual-publication controls. External availability must not create flaky merges or automatically withdraw evidence.

## Retractions and substantive reference decay

These checks cannot establish whether the publication has been corrected, retracted, superseded, or contradicted. Such a conclusion needs a separate original-source editorial review with date, publisher notice, updated interpretation and a versioned decision. Do not represent a hash change as a retraction signal, nor infer a vendor model from family-level research.

## Google Search Console

This audit does not log in to Google Search Console, submit a sitemap, change `robots.txt`, edit DNS, request indexing, or consume the owner's account credentials. Indexing and Search Console administration are outside the scope of this monitor; discovery is not synonymous with indexing.
