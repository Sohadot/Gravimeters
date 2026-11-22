# Quality, credibility and security gates — Gravimeters.com

**Independent publication control · governance CI v1.0 · 2026-11-22**

The public atlas is a sourced editorial index, **not** independent equipment calibration, supplier certification, peer review, or a validated GNSS navigation product. Automated checks complement but do not replace scientific and editorial judgment.

## Active machine gates

Every pull request, weekly scheduled read-only audit, and manual publishing run must:

1. Build all four pages and inspect required metadata, social-card files, links, sitemap, exports and navigational structure (existing smoke test).
2. Validate every instrument against the record schema, ensure measurement-type and sensor-family terms agree, and keep versioned taxonomy and data exports aligned.
3. Require each evidence record to identify its source type, claim, known limitations, publication date and review date; preprints from arXiv cannot be silently presented as peer-reviewed.
4. Reject non-HTTPS, localhost or IP-literal source links, invalid/duplicate IDs, future review dates, fabricated DOI links and unexpected escrow-link substitutions.
5. Check that workflow Action dependencies use immutable 40-character GitHub commit SHA pins, the PR job has read-only permission, and the publication workflow remains manually dispatched from `main`.
6. Check the generated public artifact for sensitive filenames, potential credential patterns and unexpected file extensions. It scans for common patterns; this is **not a complete secrets scanner**.
7. Run negative tests proving the gates fail on intentional tampering. Any failure stops the GitHub Actions job. GitHub Actions publishes a limited audit summary of record counts and pass/fail status.

## Human-only review requirements

- Verify what a primary scientific source truly establishes; a valid citation URL alone does **not** prove a claim.
- Compare device specifications only when parameters, units, conditions and citations are equivalent; never invent rankings, prices or GNSS suitability.
- Inspect source rights and license before a Zenodo deposit. A DOI is only displayed after externally verified publication and a separate controlled code review.
- Review legal, domain-transfer and paid contractual decisions with the owner. Public repository code cannot prove registrar title or escrow eligibility.
- When instruments or navigation studies change materially, conduct an independent editorial review and record the decision in the **private** Drive Decisions Log, not the public repository.

## Protection outside code

GitHub **rulesets/branch protection** must require PR review and the `check` status; a job that merely runs on pull requests can otherwise be bypassed by direct pushes. Environment protection for `github-pages`, 2FA/passkeys, and GitHub secret scanning should be enabled where available. These controls need account settings and must not be claimed as active without verification.

## Known limits and maintenance

- Offline source-URL syntax checks do not verify availability, ownership or correctness. External link freshness needs a separately reviewed verification process.
- GitHub Actions and Python dependencies are version-pinned; a future reproducible lockfile with hashes and independently reviewed advisory/secret scanning can further harden the supply chain.
- Dependabot proposes dependency updates through PRs, but does not automatically approve or deploy them.
- GitHub Pages releases are **manually initiated**, and Cloudflare remains a separate DNS/NS/security layer, never the authoritative site-build host.

## Evidence Intelligence extension (v0.3)

The public [evidence relationship methodology](EVIDENCE_RELATIONSHIP_METHOD.md) defines three **different** relationships: publication to application domain, publication to sensing family, and publication to a specifically **named instrument model**. Automated checks reject unknown relation IDs, missing source locations for model-level links, invalid evidence statuses, inconsistent source DOI metadata and unregistered application categories. These automated checks test declared **metadata and internal consistency only**; they do not determine whether a scientific paper actually supports a summarized result, whether a paper has been retracted, or whether a model's claimed performance has been independently verified.
