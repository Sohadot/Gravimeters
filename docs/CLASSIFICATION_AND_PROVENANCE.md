# Classification, provenance and reuse — Gravimeters.com

**Independent editorial taxonomy v0.1 · 2026-11-22**

This is a source-linked index of gravity-measurement instruments. It is **not** an IAG/BGI publication, calibration standard, manufacturer endorsement, vendor partnership or equipment performance certification.

## Distinct axes

A gravimeter may use **relative or absolute** measurement; this is the measurement-mode facet. Its sensing principle (quartz-based, free-fall interferometry, cold-atom interferometry or superconducting) is a different facet. Deployment setting is separate again. Labels from different facets must not be combined into one exclusive set of classes.

A gravity **gradiometer** measures spatial gradients of gravitational acceleration and is related but distinct. Multi-function instruments require model-specific evidence before they can be assigned both classes.

## Source and evidence standards

Three manufacturer-source-linked instrument records and one explicitly identified navigation research preprint comprise version 0.1. Record IDs, links, editorial review dates and category labels are retained. This is not proof that the maker's claims have been independently reproduced.

Public machine-readable dataset: https://gravimeters.com/data/atlas.json  
Public record field schema: https://gravimeters.com/data/schema/instrument.schema.json

Build-time validation checks required fields, allowed classification terms, ID uniqueness and source URL format. Future releases must change the explicit dataset version and explain material taxonomy shifts. Missing values are not fabricated. No third-party logos, product literature or original research works are relicensed by this metadata export.

## Navigation evidence is distinct from device capability

A demonstrated gravity-aided navigation result depends on sensor measurements, reference maps, inertial data, algorithms and environmental limits. It does not prove that a single gravimeter independently provides position or automatically replaces GNSS. Distinguish preprint, peer-reviewed study, field test and commercial announcement.

## Scientific context (not affiliation)

- BGI gravity databases: https://bgi.obs-mip.fr/gravity-databases/
- BGI international gravity reference: https://bgi.obs-mip.fr/international-gravity-reference-frame/

No DOI or Zenodo publication is implied by this initial data export. DOI issuance awaits a rights-reviewed and materially reusable frozen release.

## Comparison scope and interpretation (v0.2)

The public matrix compares only documented **instrument model**, **measurement mode**, **sensing principle**, **deployment context**, and **original-source link**. It does not compare accuracy, cost, readiness, frequency response, calibration, performance or suitability, because primary sources do not describe those fields in a sufficiently harmonized manner. Different deployment contexts are not direct substitutes. A future technical comparison must cite each specification with conditions and source revision.

Initial public example records and their source references are attributable to the original manufacturers, not to any endorsement of this project. The four v0.2 records are: Micro-g LaCoste A10, Micro-g LaCoste gPhoneX, GWR iGrav, and ZLS Burris. Their published source links and editorial-review date appear in the JSON export.

**Evidence association boundary:** A quantum gravimeter employed in an external navigation experiment is not presumed to be the Exail AQG (or any other listed commercial instrument). Evidence-to-model links require documented hardware identification and an explicit citation. A link to an instrument **class** does not establish product-level performance.
