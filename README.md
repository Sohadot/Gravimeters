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

**No merge of PR #1 and no initial deployment without explicit owner approval.** **Publishing doctrine:** GitHub is the canonical development, review, CI and publication platform. The intended public hosting target is **GitHub Pages**, using the tested static output from `dist/` and an owner-approved publication workflow. **Cloudflare is the separate NS/DNS, proxy/security and TLS layer**, not the source of truth or the primary deployment host. Configure `gravimeters.com` as a GitHub Pages custom domain and verify HTTPS/domain state before applying Cloudflare DNS/proxy settings. No Cloudflare Pages deployment is authorized. Development and evidence review are not affiliation or endorsement by any manufacturer.

## Acquisition, verification and share previews

- `data/links.json` contains the verified public GitHub URL and a `null` Zenodo record URL until an actual dataset release exists. A reserved draft DOI is **not** a public citable record. When a Zenodo record is published, insert its exact verified HTTPS URL in `zenodo_record_url`; the acquisition page automatically links to it.
- The acquisition route describes an **optional** independent escrow procedure, not an active transaction, provider partnership, existing escrow account or guaranteed transfer. A buyer and seller must separately agree to the terms, settlement service, asset scope and fees.
- Four 1200 × 630 original JPEG share images are available in `static/assets/og-*.jpg`; HTML includes per-page Open Graph and X image metadata. On an actual deployment, test their absolute HTTPS URLs and the rendered previews using platform share-debuggers. The local build alone cannot prove platform cache behavior.
- A non-deploy helper `scripts/render_social_assets.py` can regenerate the images from the project-created `social-field-source.jpg` with Pillow and local fonts; it is not a build dependency.
- `agent@sohadot.com` is owner-provided but not yet verified for incoming mail. No sale, referral, broker or escrow agreement is implied.

**Publication gate remains explicit owner approval before merging or deploying PR #1.**

## GitHub-first deployment order (owner-gated)

1. Complete visual, editorial, accessibility and link review in the PR. Pull-request CI never deploys.
2. Obtain the owner's explicit approval before merging PR #1 and before the first public release.
3. Configure the repository's **Pages publishing source = GitHub Actions**; establish a protected `github-pages` environment where supported.
4. The separate `Publish approved site to GitHub Pages` workflow uses **manual dispatch on `main` only**, runs the offline tests, uploads only `dist/` and deploys to GitHub Pages. No push, pull request or CI success automatically publishes.
5. Add the custom domain `gravimeters.com` to GitHub Pages settings **before changing DNS**, and validate domain ownership and GitHub Pages HTTPS. Follow verified current DNS instructions for the apex and `www`; do not switch production DNS without approval.
6. Set up Cloudflare NS/DNS and applicable protection **as a secondary layer**, preserving existing mail/MX records. DNS delegation by itself is not protection; verify TLS and proxy compatibility with the GitHub Pages origin.
7. Check HTTPS, redirects, all four routes, source links, JPG social previews, robots, sitemap and actual contact-email delivery after the authorized launch.

Neither a passing PR check nor the presence of this deployment workflow permits merging, running production deployment, switching NS or sending outreach.
