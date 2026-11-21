# Gravimeters.com

Public source for a small, independently maintained atlas of gravity-measurement instruments and published navigation evidence. **This repository is public; no internal strategy, commercial leads, private correspondence or secrets belong here.**

## Build locally (also works in GitHub Codespaces)

```bash
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/smoke_test.py
```

Generated output is in `dist/`. Publish that directory to an authorized static host only **after owner approval of PR #1**. This PR does not change domain DNS, create mail routing or publish to production.

## Owner-friendly edits

- Change entries in `data/instruments.json` or `data/evidence.json` with GitHub's web editor, keeping valid JSON and a link to the original source.
- Change the page layout in `templates/site.html`; visual styling is in `static/site.css`.
- Run the build and smoke test. Review every technical claim against its linked source before merging.
- Review `docs/EDITORIAL_POLICY.md` before adding a manufacturer or a new trial.

Current contact CTA uses `agent@sohadot.com`, provided by the owner but **not yet delivery-tested** for this site. Do not claim a dedicated Gravimeters mailbox is active until routing and inbound delivery are verified.

## Publishing gate

**No merge of PR #1 and no initial deployment without explicit owner approval.** Planned host: Cloudflare Pages or a verified existing static hosting configuration. Development and evidence review are not affiliation or endorsement by any manufacturer.

## Acquisition, verification and share previews

- `data/links.json` contains the verified public GitHub URL and a `null` Zenodo record URL until an actual dataset release exists. A reserved draft DOI is **not** a public citable record. When a Zenodo record is published, insert its exact verified HTTPS URL in `zenodo_record_url`; the acquisition page automatically links to it.
- The acquisition route describes an **optional** independent escrow procedure, not an active transaction, provider partnership, existing escrow account or guaranteed transfer. A buyer and seller must separately agree to the terms, settlement service, asset scope and fees.
- Four 1200 × 630 original JPEG share images are available in `static/assets/og-*.png`; HTML includes per-page Open Graph and X image metadata. On an actual deployment, test their absolute HTTPS URLs and the rendered previews using platform share-debuggers. The local build alone cannot prove platform cache behavior.
- A non-deploy helper `scripts/render_social_assets.py` can regenerate the images from the project-created `social-field-source.jpg` with Pillow and local fonts; it is not a build dependency.
- `agent@sohadot.com` is owner-provided but not yet verified for incoming mail. No sale, referral, broker or escrow agreement is implied.

**Publication gate remains explicit owner approval before merging or deploying PR #1.**
