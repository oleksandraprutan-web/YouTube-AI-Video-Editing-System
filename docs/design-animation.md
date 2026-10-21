# Design, Claude Design, animation and motion graphics

Design begins after the cut is approved. The transcript of the approved WAV determines what visuals explain and when they appear. An earlier recording script is only a reference.

## Unbranded starter library

The [design pack](../templates/design/README.md) contains eight complete, static HTML layouts and a local [gallery](../templates/design/index.html). The layouts cover process, comparison, chart, timeline, layers, code, evidence, and recap. They have no logos, promotional copy, external fonts, or media dependencies.

Use the [filled briefs](../templates/design/briefs) to see how to specify actual board content and evidence. The [prompt sequence](../templates/design/prompts) covers transcript-to-brief, brief-to-HTML, and visual review. These are editable public templates, not private production skills.

The new boards have a static `seek(seconds)` adapter for the renderer. Their sample timeline is [design-starters-timeline.json](../examples/design-starters-timeline.json); its six-second scene lengths are demonstration values. Use real final-cut word timings for production. The earlier [generic board](../templates/board/index.html) remains available as a minimal fade example.

## Design handoff

Fill `templates/design-brief.md`: audience, canvas, content per board, visual hierarchy, palette, fonts, camera safe area, source references and accessibility. Paste `templates/claude-design-prompt.md` with that brief and transcript into Claude Design, or use your preferred designer or agent. Claude Design is an optional external tool; this repository has no automatic Claude Design integration and bundles no proprietary styles or prompts.

Download HTML boards and assets into `04-boards/`. Use local assets and fonts you have permission to redistribute. Review boards in the target aspect ratio before animating.

## Motion contract

Each board exposes `window.seek(seconds)` where seconds are local to that board. The same time must always produce the same pixels, even when seeking backward. Avoid autonomous timers, random state, live external assets, and CSS animations that ignore the timeline. Keep camera space reserved. Use project preferences for motion; the starter board uses a simple opacity entrance, not a finished branded look.

The timeline has canvas, fps, duration and ordered scenes with `start`, `end`, and `file`. Scene paths are relative to the timeline JSON. Gaps render white. Overlaps are rejected. Word timings are measured on the approved final audio, not source-take time.

## Render a board track

```bash
uv run --with playwright --with imageio-ffmpeg python -m playwright install chromium
uv run tools/render_boards.py examples/board-timeline.json .local/board-track.mp4
```

The renderer seeks the HTML at every frame and writes a silent H.264 track. It never edits the approved WAV. HTML is code: render only boards you trust. Add the board track in your NLE alongside the approved cut and WAV. Use the safe area you specified in the brief to place the camera. Validate that narration and visual changes stay aligned throughout.

For another motion framework, retain the same deliverables: editable sources, timing manifest, silent graphics track and a review report. Private skill implementations are intentionally absent; customize the placeholder animation skill for your own production method.
