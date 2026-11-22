# Activate enforceable GitHub branch and release protection

**Pending account setting — no repository workflow can enforce its own merge requirements.**

In `Sohadot/Gravimeters` → Settings → Rules → Rulesets, create an active branch ruleset targeting `main`:

- Require a pull request before merging. Require an independent approving review only when a real second reviewer exists; do not deadlock a sole-maintainer repository by requiring an unavailable reviewer.
- Require status checks before merge: select GitHub Actions check **`check`** from `Build and smoke-test (no deploy)`; require the branch to be current with `main` if practical.
- Block force pushes and branch deletion; disable bypasses for day-to-day actors wherever available.
- Consider requiring Code Owner review for future sensitive files *after* real owner/team identities are verified, not by inventing a GitHub identity.

For Settings → Environments → `github-pages`, add eligible reviewers or review protection where available. Keep the existing GitHub Pages publication explicitly manual, on `main`, and preserve its permissions and OIDC separation.

In Settings → Security / Code security, enable secret scanning, push protection, and Dependabot alerts where eligible. Protect the GitHub organization account with passkeys/2FA.

**Record actual settings/screenshots and results in the private Drive Decisions Log** before representing these protections as enforced. GitHub Actions CI can block the workflow on failing checks, but without rulesets a sufficiently privileged repository actor can still merge/push bypassing CI.
