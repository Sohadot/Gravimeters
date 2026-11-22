# Evidence relationships and source credibility — v0.3

**Public methodology · 2026-11-22**

This is an editorial graph of publicly reported research. It is not a scientific validation service, independent replication, equipment certification or endorsement by authors, journals or manufacturers.

## Typed relationships

| Relationship | Record field | Meaning | Prohibited inference |
| --- | --- | --- | --- |
| Application → evidence | `application_ids` | Authors' study belongs to the named research/application domain | Other deployments share the result |
| Sensor family → evidence | `sensing_families` | Sensing principle discussed or applied in the study | A particular commercial product was used |
| Named instrument → evidence | `linked_instruments` | The source explicitly names a cataloged model; link records the relevant section | Product endorsed, calibrated or rated independently |

A relationship to a **class** must never automatically be promoted to a relationship to a **model**. `model_explicitly_named_in_source` requires a precise `source_section` and editorial verification against the actual research source. The automated gate checks that a source section exists; it cannot independently certify that the text genuinely supports the claim.

## Evidence status and original DOI

- `preprint` means not presented as peer-reviewed here. The 2026 maritime navigation study is an arXiv preprint; findings remain context-dependent.
- `peer_reviewed_article` is an editorial classification for a published journal article with a verified article URL and a source DOI. Editorial checks do not substitute for scholarly review or retraction monitoring.
- `source_doi` is the original authors' publication DOI. **No Gravimeters.com dataset DOI or Zenodo DOI has been issued.**
- Every record distinguishes an author's reported outcome (`claim`) from important non-generalizability (`boundary`), source publication date, and our editorial review date.

## Initial, manually source-checked associations

1. [2026 maritime gravity-aided navigation preprint](https://arxiv.org/abs/2608.25563): navigation application and cold-atom family only. No commercial instrument model asserted.
2. [Bidel et al. 2018, marine atom interferometry](https://www.nature.com/articles/s41467-018-03040-2): marine survey and cold-atom family only. No commercial model asserted.
3. [Shettell et al. 2024, hybrid gravity survey](https://www.nature.com/articles/s41598-024-57253-1): paper's methods name the Scintrex CG6. The separately described atomic reference gravimeter is **not** mapped to Exail AQG.
4. [Greco et al. 2024, Sicily reference network](https://www.nature.com/articles/s41597-024-03177-4): methods explicitly name the Scintrex CG-6 for gravity-difference transfers and vertical-gradient measurements. This does not convert the CG-6 into a gravity gradiometer product.

## Editorial gates

- Preserve source-type label, `source_doi` as a *source* reference, publication/review dates and unique IDs.
- Require an application reference to a registered application, sensing family to a controlled taxonomy, model reference to a registered instrument, and an explicit source-location note for model citations.
- Do not infer navigation certification from the presence of a gravimeter in a research paper.
- Recheck source availability, citation validity and potential corrections or retractions periodically. Current automated CI validates internal consistency, **not** live link reachability or the scientific conclusions.
- Public export retains third-party rights notices and does not reproduce copyrighted paper figures or substantial article text.

The public source files and revision history can be examined in [GitHub](https://github.com/Sohadot/Gravimeters); the private decisions log remains in an owner-only Google Drive folder.
