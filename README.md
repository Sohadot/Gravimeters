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

**No merge of PR #1 and no initial deployment without explicit owner approval.** **Publishing doctrine:** GitHub is the canonical development, review, CI and publication platform. The intended public hosting target is **GitHub Pages**, using the tested static output from `dist/` and an owner-approved publication workflow. **Cloudflare is the separate DNS/nameserver, proxy/security and TLS layer**, not the source of truth or the primary deployment host. Configure `gravimeters.com` as a GitHub Pages custom domain and verify GitHub's HTTPS/domain state before applying Cloudflare DNS/proxy settings. No Cloudflare Pages deployment is authorized. Development and evidence review are not affiliation or endorsement by any manufacturer.

## Acquisition, verification and share previews

- `data/links.json` contains the verified public GitHub URL and a `null` Zenodo record URL until an actual dataset release exists. A reserved draft DOI is **not** a public citable record. When a Zenodo record is published, insert its exact verified HTTPS URL in `zenodo_record_url`; the acquisition page automatically links to it.
- The acquisition route describes an **optional** independent escrow procedure, not an active transaction, provider partnership, existing escrow account or guaranteed transfer. A buyer and seller must separately agree to the terms, settlement service, asset scope and fees.
- Four 1200 × 630 original JPEG share images are available in `static/assets/og-*.png`; HTML includes per-page Open Graph and X image metadata. On an actual deployment, test their absolute HTTPS URLs and the rendered previews using platform share-debuggers. The local build alone cannot prove platform cache behavior.
- A non-deploy helper `scripts/render_social_assets.py` can regenerate the images from the project-created `social-field-source.jpg` with Pillow and local fonts; it is not a build dependency.
- `agent@sohadot.com` is owner-provided but not yet verified for incoming mail. No sale, referral, broker or escrow agreement is implied.

**Publication gate remains explicit owner approval before merging or deploying PR #1.**

## GitHub-first deployment order (owner-gated)

1. Complete visual, editorial, accessibility and link review within this PR. CI does not publish.
2. Obtain the owner's **explicit approval** to merge PR #1 and to carry out the initial public release.
3. Configure a GitHub Actions → GitHub Pages publication from the approved `main` revision, taking `dist/` from `python scripts/build.py` (do not publish source data, internal files, or repository root as a substitute).
4. Attach the custom domain `gravimeters.com` to GitHub Pages, using the domain's documented verification and DNS records; avoid DNS cutover until the site serves correctly and TLS is verified.
5. Delegate the domain's authoritative nameservers to Cloudflare only after reviewing existing DNS/email records. Configure DNS and applicable proxied protection, TLS/SSL modes and cache rules for a GitHub Pages origin; **NS delegation alone is not protection**.
6. Verify public HTTPS, canonical redirects, all four routes, social preview image URLs, `robots.txt`/sitemap and contact email delivery. Publish DOI links only after a real Zenodo record exists.

**Hard rule:** GitHub Pages owns publication; Cloudflare supplements routing and protection. Neither a successful PR check nor the use of Cloudflare NS grants permission to merge, deploy, change nameservers or enable email routing.
