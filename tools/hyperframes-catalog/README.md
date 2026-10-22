# HyperFrames catalog (vertical, lawyer brand)

Registry items from heygen-com/hyperframes (Apache-2.0), restyled for 1080×1920, navy #02064A / orange #F47A3A, Montserrat, Polish text:

| Code | Item | Changes |
|---|---|---|
| HF1 | `count-up` (component) | Polish thousands separator ("2 500 zł"), orange via `--brand`, glow |
| HF2 | `mk-specs-list` (block) | 1080×1920, dark scheme, navy top scrim, orange underline, Montserrat 900, 4 rows |
| HF3 | `lt-kicker-name` (block) | 1080×1920, orange kicker + baseline, Montserrat, placed above captions |
| HF4 | `marker-checklist-card` (component) | full-frame cutaway on navy (no Polish diacritics in marker font) |
| HF5 | `caption-highlight` (component) | 1080×1920, orange word highlight, words from transcript |

Background footage `assets/bg.mp4` is not committed — put a clip there (re-encode with `-g 30`). Render: `npx hyperframes@0.8.185 render --output renders/catalog.mp4`.
