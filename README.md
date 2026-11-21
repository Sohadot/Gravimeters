# Gravimeters.com

**Public site:** https://gravimeters.com/  
**Source of truth:** [Sohadot/Gravimeters](https://github.com/Sohadot/Gravimeters)

Gravimeters.com is an independently maintained, source-linked atlas of gravity-measurement instruments and published evidence concerning gravity-aided navigation. This repository is public: **no internal strategic plans, acquisition correspondence, buyer details, credentials or secrets belong here.**

## Release status

- The inaugural public site was integrated through [PR #1](https://github.com/Sohadot/Gravimeters/pull/1) on **2026-11-21**.
- GitHub Pages published its generated static-site artifact on **2026-11-21** via [manual release workflow](https://github.com/Sohadot/Gravimeters/actions/runs/44950422020).
- Screenshots supplied after deployment show the live conceptual homepage instead of the earlier repository README.
- **Pending independent verification:** external crawl of all routes, HTTPS assets on social-platform scrapers, and receipt/reply capability for the published contact address.
- **Not claimed:** independent device testing, vendor partnerships, published Zenodo DOI, operating escrow transaction, or verified lead forwarding.

## Architecture and publishing doctrine

**GitHub** is authoritative for source, editorial changes, review, CI, version history and **GitHub Pages** publication. **Cloudflare** is a separate optional NS/DNS, TLS and security layer, not the build host.

- Build system: Python 3.11 + Jinja2; editable instrument and evidence data in JSON.
- Public routes: `/`, `/instruments/`, `/navigation/`, `/acquisition/`.
- Deployment: `workflow_dispatch` on approved `main` releases. No automatic publishing on every commit.
- Generated `dist/` is uploaded to Pages; internal strategic material is never included.

## Build and verify locally

```bash
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/smoke_test.py
```

Only generated static files in `dist/` are eligible for publication. Read [GitHub Pages release runbook](docs/GITHUB_PAGES_RELEASE_RUNBOOK.md) before running a release.

## Editing and provenance

- Instrument records: `data/instruments.json`
- Navigation evidence records: `data/evidence.json`
- Verified public links, including future Zenodo record (currently `null`): `data/links.json`
- Site templates: `templates/site.html`
- Visual styles: `static/site.css`
- Original social-preview assets: `static/assets/og-*.jpg`

Technical statements must remain traceable to their original sources. See [public editorial policy](docs/EDITORIAL_POLICY.md). Gravimeters and gravity gradiometers are not interchangeable categories. Navigation claims are evidence-linked and do not imply gravity alone provides positioning.

## Acquisition and contact

The [acquisition page](https://gravimeters.com/acquisition/) explains the optional independent escrow process and its limits. No active escrow account or partnership is represented. Public GitHub history is inspectable, but does not establish private domain title or transfer eligibility; due diligence remains necessary.

For confidential strategic inquiries and corrections, the owner-provided address is **agent@sohadot.com**; inbound delivery has **not yet been live-tested** for this site.

## Release controls

Substantial navigation-evidence changes require separate editorial/owner review. Production releases remain deliberately owner-triggered; an accepted PR alone does not initiate deployment.
