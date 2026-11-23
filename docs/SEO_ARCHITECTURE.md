# Search architecture and release discipline — Gravimeters.com

**Technical SEO foundation v1.0 · 2026-11-23**

## Editorial positioning

Gravimeters.com is a source-linked editorial gravity-instrument atlas and evidence registry, not a manufacturer, certification body, GNSS replacement product, independent calibration lab or scientific journal. Its topical pillars are (a) gravimeter classes and operating contexts, (b) gravity-aided navigation with evidence limits, (c) source-level scientific evidence and application relationships. No ranking, invented specs, fabricated FAQ, keyword stuffing or scaled near-duplicate pages.

## One route/metadata source of truth

\`data/seo_manifest.json\` provides canonical route, page ID, title, description, social preview and explicit \`indexable\` flag. \`scripts/build.py\` validates it, renders those values to HTML, and lists only its indexable canonical routes in \`sitemap.xml\`. \`robots.txt\` is stored in \`static/\` and shipped unchanged into the generated artifact. Do not invent \`lastmod\`; use only real editorial revision timestamps if later supported.

All **five existing** pages remain indexable in this release. This explicitly preserves the existing Search Console sitemap state; any future decision to exclude the acquisition route, add indexable device-specific pages or split datasets requires documented justification, owner-controlled release, and measurable unique search intent. A future nonindexable route must emit \`noindex,follow\` and be absent from the sitemap. A sitemap entry is a discovery hint, not an indexing or ranking guarantee.

## Schema.org semantics

Use a coherent \`@graph\`: \`WebSite\` plus a page-level \`WebPage\` or \`CollectionPage\`, \`BreadcrumbList\` on internal routes, and a restrained \`Dataset\` description on the evidence registry because the machine-readable v0.3.0 JSON export is truly available. Its \`DataDownload\` points to \`/data/atlas.json\`. This is an **editorial source index**, not original instrument observations, an official dataset, a standards authority, third-party content ownership or a Zenodo publication. Do not fabricate \`license\`, \`review\`, \`rating\`, \`SearchAction\` or \`sameAs\` claims.

**Important:** Google documents Dataset structured data for **Dataset Search**; it does not guarantee ordinary Google Search rich results. Structured data helps a machine interpret truthful facts but does not create scientific authority on its own.

## Deterministic gates on pull requests and manual releases

\`scripts/seo_gate.py\` audits all built routes and fails if canonical, title, description, robots, OG, social image existence, Schema.org, breadcrumb, dataset-version/distribution or sitemap differs from the manifest; if robots blocks the root; if indexability conflicts with the sitemap; or if an unexpected route is built. \`scripts/smoke_test.py\` calls this gate and therefore enforces it on the protected \`check\` job and the separately manually triggered Pages deployment. The \`tests/test_seo_gate.py\` negative tests prove this gate refuses intentionally broken SEO states.

This is an **offline release-quality gate**, not a guarantee of indexing, CWV, ranking, external HTTP redirects, institutional trust or the scientific correctness of sources.

## Search Console operating boundary

The Search Console property and its indexation evidence are administered separately from this public source repository. No workflow here can submit, resubmit, inspect or change a Search Console property; these account actions require their own explicit authorization. Submission of a sitemap or discovery of a URL must never be represented as confirmed indexation. Owner-specific operating schedules and administrative decisions belong in the **private** governance register, not this public document.

## Performance and editorial growth gates

1. Measure mobile/desktop Core Web Vitals on the actual site before claiming speed. A build test alone proves nothing about LCP, INP or CLS.
2. Recheck source provenance and link integrity through the separate read-only Reference Integrity workflow; never automatically invalidate a paper due to HTTP failure.
3. Identify query intent using factual source/keyword research after the hold; prioritize high-value reference destinations only when they can offer uniquely verified information, real comparative context and primary citations.
4. Track Search Console impressions, indexed pages and queries after 2026-11-30, noting that five discovered URLs do not equal five indexed URLs.
5. Promote only substantial, reviewable, source-backed pages and clear internal navigation; no mass-generated page multiplication.
6. No synthetic backlinks, bulk outreach, paid links, fake authorship or unsupported institutional affiliation.
7. GitHub is always the source, test and manual Pages publication authority; Cloudflare remains DNS/security only.

## Official guidance

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- https://developers.google.com/search/docs/appearance/structured-data/dataset
