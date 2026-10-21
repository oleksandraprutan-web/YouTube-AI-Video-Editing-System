# Unbranded explainer design pack

Open [index.html](index.html) locally for the visual gallery. GitHub shows HTML source; download or clone the repo to preview it in a browser. No build step, external fonts, network requests, logos, footage, or accounts are needed.

## Choose a layout

| Board | Use it to explain |
| --- | --- |
| [Process](boards/01-process.html) | Inputs, actions, and outputs |
| [Comparison](boards/02-comparison.html) | Two options using matching criteria |
| [Chart](boards/03-chart.html) | Values on a shared zero-based scale |
| [Timeline](boards/04-timeline.html) | Phases and decision points |
| [Layers](boards/05-layers.html) | Responsibilities and dependencies |
| [Code](boards/06-code.html) | A specific field or line with context |
| [Evidence](boards/07-evidence.html) | A claim, observation, and source |
| [Recap](boards/08-recap.html) | Three actionable takeaways |

These are complete static starter layouts, not a finished video or a private production skill. They use a neutral palette and system fonts. All copy and data are examples. The `seek(seconds)` function is intentionally static so the existing renderer can consume the boards; add motion after design approval.

## Briefs and prompts

Start with [the reusable brief](../design-brief.md), or adapt a filled example:
- [Explain a process](briefs/process.md)
- [Compare two approaches](briefs/comparison.md)
- [Explain a measurement](briefs/evidence.md)

Then use [transcript to brief](prompts/transcript-to-brief.md), [brief to HTML](prompts/brief-to-html.md), and [review the boards](prompts/review.md). [The design-tool prompt](../claude-design-prompt.md) works with an HTML-capable design assistant.

## Customize and export

1. Copy selected HTML files to your project's `04-boards/`. Every board is self-contained.
2. Edit the headline, labels, source notes, and SVG data. Update accessible chart descriptions with the values. Never present sample values as real measurements.
3. Set the CSS variables at the top of each file for your palette and type. The default canvas is 1920 × 1080. Content is kept out of the lower-right camera area: x=1280, y=584, width=576, height=432. Add `?guides` in a browser to inspect it; leave guides off for export.
4. Review text at small playback sizes, source accuracy, and camera clearance. Resize/reflow deliberately for another aspect ratio; these files do not automatically become vertical boards.
5. Use `examples/design-starters-timeline.json` from the repository root to render all eight as a silent track. Its six-second scenes are demonstration timings, not recommended narration timing. Scene paths are relative to the JSON file; update them if you copy the timeline elsewhere.

```bash
uv run tools/render_boards.py examples/design-starters-timeline.json .local/design-starters.mp4
```

Install the renderer dependencies and browser as described in [the design guide](../../docs/design-animation.md). Preserve the approved narration. Add any final motion through deterministic `seek(seconds)` states after board approval.

## Reference and branding boundary

The owner-supplied explainer board library was a layout reference for process, comparison, chart, sequence, layered-system, code, evidence, and recap patterns. This pack is freshly authored and does not redistribute that library. Original branded CSS, identities, product logos, community links, promotions, source screenshots, footage, personal stories, and episode-specific numbers are not included. The original reference stays separate for future consultation.

There are no attribution banners, product endorsements, waitlist links, or promotional footers inside this pack. Tool names in workflow documentation identify optional software; they are not part of the board artwork. Private skill contents remain excluded. These new templates follow the repository's MIT code/template license.
