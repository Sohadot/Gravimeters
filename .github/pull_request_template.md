## Change purpose and durable user value
Describe the useful improvement rather than page count or promotional claims.

## Evidence and provenance
- [ ] Each new instrument or scientific claim is supported by an original source and review date.
- [ ] Distinguishes gravimeter vs. gravity gradiometer and measurement mode vs. sensor principle.
- [ ] Avoids unverified performance, manufacturer endorsement, pricing, peer review or published Zenodo DOI claims.

## Governance and safety
- [ ] `python scripts/smoke_test.py` passes.
- [ ] `python scripts/governance_gate.py` and `python -m unittest discover -s tests` pass.
- [ ] No credentials, sensitive correspondence, private decisions or owner data in this PR or `dist/`.
- [ ] Security-impacting workflow changes are explicitly reviewed.
- [ ] No outreach or direct buyer/vendor contact is initiated.

## Release decision
An accepted PR **does not** publish to GitHub Pages. Publication remains separately and intentionally triggered from approved `main`.
