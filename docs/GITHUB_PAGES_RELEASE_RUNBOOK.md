# Public release procedure — GitHub Pages first

**Status: INAUGURAL RELEASE DEPLOYED on 2026-11-21** through [GitHub Actions](https://github.com/Sohadot/Gravimeters/actions/runs/44950422020). Owner-supplied browser screenshots show the intended homepage. This runbook governs later releases and unresolved public validation; it does not authorize automatic publication. Mail delivery, external OG crawler previews and the remaining page-by-page public HTTP checks are not yet independently confirmed.

## Governing architecture

- **GitHub** maintains source, editing, pull-request review, tests, releases and GitHub Pages publication.
- **Cloudflare** is the separate domain NS/DNS, security, proxy (when compatible), caching and TLS layer. Never substitute Cloudflare Pages as the site host.
- Internal management plans, private correspondence, registrar records, acquisition negotiations and secrets must stay out of the public repository and the `dist/` artifact.

## Approval gate and release record

The owner delegated ordinary technical project management; PR #1 was squash-merged and the initial site manually deployed through GitHub Pages on 2026-11-21. This historic release does not authorize automatic future publishing. Subsequent releases follow applicable owner gates and editorial policy; public navigation/evidence overhauls require a separate approval gate.

## Preflight checklist

1. Ensure the latest PR changes have passed the CI smoke check and all four page routes have been visually inspected on mobile and desktop.
2. Check technical claims against their linked published sources; make no unsupported endorsement or GNSS-replacement claim.
3. Verify that the four JPEG social-preview images are accessible at the absolute URLs in metadata after publication.
4. Verify `agent@sohadot.com` receives messages and the owner can reply. Until then, note the unverified contact state; do not claim verified inbound acquisition handling.
5. Check the owner-approved terms for domain acquisition, possible escrow, and DOI: no escrow partnership, transaction or unpublished DOI may be suggested as active.
6. Record the owner’s approval before any public merge/deploy/DNS change.

## GitHub Pages release (owner-approved only)

1. Merge the approved PR to `main` using the agreed review process.
2. In GitHub repository **Settings → Pages**, choose **GitHub Actions** as the publishing source. If eligible, configure protection/review rules for the `github-pages` environment.
3. In GitHub Actions, run **Publish approved site to GitHub Pages** using **Run workflow → main**. The workflow builds `dist/`, runs smoke tests and uploads only that directory with GitHub's Pages artifact action. There is no `push` or `pull_request` publication trigger.
4. Verify the deployment from the GitHub Actions run and GitHub Pages settings; do not assume a successful build means the public domain resolves.
5. Add `gravimeters.com` as the custom domain in GitHub Pages settings *before* changing DNS, following current GitHub documentation. Check GitHub's domain ownership verification if requested.
6. With owner approval, configure GitHub Pages apex and optional `www` DNS records in the domain's authoritative DNS. If NS must move to Cloudflare, preserve existing MX, TXT, SPF, DKIM, DMARC and other active records; validate mail continuity. Leave records **DNS only** initially while verifying GitHub Pages HTTPS issuance; evaluate proxied mode separately for compatibility and security benefits.
7. Confirm the expected HTTPS certificate and redirect behavior for both apex and `www`, with `gravimeters.com` as canonical host. Test navigation, acquisition, atlas, sources and all four social cards through an external scraper where available.
8. Verify sitemap, robots, canonical tags, structured data and HTTPS content. Monitor after launch for email delivery, broken external references, and platform preview caches.

## Rollback

For a bad GitHub Pages content release, revert the content through GitHub with an auditable commit or redeploy a known approved SHA. Do not force-push `main`. DNS/NS rollback is a separate owner-approved change; preserve mail and domain security. Keep the internal decision trail private.

## Operational references

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https
