# Security policy — Gravimeters.com

This public repository is the GitHub Pages source for a static, independent reference atlas. Report potential security defects privately wherever possible. Do not publish credentials, personal data, private acquisition correspondence or reproducible exploit details in public GitHub issues.

The repository's owner-provided address is `agent@sohadot.com`; delivery and response have not yet been independently verified. GitHub private vulnerability reporting may be used if enabled by the owner. Neither channel is a guarantee of response time.

Scope: unintended disclosure of internal content, compromised data/source integrity, supply-chain vulnerabilities, unsafe publishing workflow changes, third-party code injection and misleading security/escrow/DOI claims. Reports about scientifically incorrect technical assertions should use a documented source and the editorial correction channel.

We do not collect instrument procurement inquiries through a custom server. The website's acquisition page describes optional independent escrow; it does not operate an escrow platform. The public repository and automated gate do not certify domain ownership or the security of external vendors.

## Change security rules

- No production auto-publish on commits, PRs or schedules; only manual `workflow_dispatch` from `main`.
- Treat PR code as untrusted; PR checks run without write privileges and without application secrets.
- All third-party GitHub Actions use full commit SHAs. Dependabot raises update PRs; updates are not automatically merged or published.
- Only generated `dist/` may be published. The private Decisions Log, strategic plans, customer information, API credentials and owner correspondence are excluded.
- `main` should have a GitHub ruleset requiring PRs and the **`check`** job before merging. **This is not active until the owner configures it in repository settings.**
