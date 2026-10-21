# AI Video Editing System

**An open-source workflow for recording, AI-assisted editing, design, Claude Design, animation, motion graphics, and the final editor handoff.**

Eyeline connects the script you read, the takes you record, the source clips you cut, and the visuals you design. The workflow keeps its decisions in readable Markdown and JSON so you can use your own AI agent, change the rules, and keep editing by hand.

![Eyeline Edit — preview, transcript and source-linked timeline](docs/media/editor-demo.gif)

[Quick start](#quick-start) · [Workflow](docs/workflow.md) · [Design & motion](docs/design-animation.md) · [JSON formats](docs/formats.md) · [Customize the skills](docs/customization.md) · [Architecture](docs/architecture.md)

## What is included

| Part | What it does |
| --- | --- |
| **Eyeline teleprompter** | Read a script, follow your voice, record microphone audio, mark flubs, track attempts, and optionally sync a display over your local network. |
| **Eyeline Edit** | Review source-linked clips, inspect waveforms and word timings, adjust cut edges, relink camera originals, and export video/audio. |
| **AI editing tools** | Transcribe takes, estimate camera sync and drift, build full-take proxies, propose a candidate cut, and report possible transcription or edge issues. |
| **Agent instructions** | Separate recording, cutting, review, design, animation, and editor handoff responsibilities. Use with a coding agent that can read files and run commands. |
| **Design / Claude Design workflow** | Turn the approved transcript into a visual brief and HTML boards using your design tool of choice, including Claude Design. |
| **Animation / motion graphics** | A generic seekable board template, JSON timeline, and local frame renderer for narration-aligned graphics. |
| **Editor handoff** | A predictable folder tree, approved audio, source mapping, rendered boards, captions, and a finishing checklist for Resolve, Premiere, or another editor. |
| **Placeholder skills** | Fresh, intentionally unconfigured templates you can fine-tune for your own voice, design, pacing, and motion. No private production skills are included. |

This is an early public release, not an unattended one-click editor. Cutting decisions need human review. Speech recognition can turn a mispronounced word into a correctly spelled transcript, and waveform silence is not proof that a word is finished. [Read the limits](docs/cutting.md).

## Quick start

Install **Python 3.10+** and **uv** from their official installers. Chrome or Edge is recommended for browser speech recognition. No API key is required to launch either app.

```bash
git clone https://github.com/sirioberati/AI-Video-Editing-System.git
cd AI-Video-Editing-System

# Teleprompter — open http://localhost:5317
python3 apps/teleprompter/server.py
```

On Windows, use `py` in place of `python3`. Projects are saved to `~/Eyeline/Projects` by default. Set `EYELINE_DATA` before starting to use another drive. Keep the terminal running.

In a second terminal:

```bash
# Editor — open http://localhost:5320
uv run apps/eyeline-edit/edit_server.py
```

The editor needs an Eyeline project with a cut plan and full-take playback proxies. For a first look without recording anything:

```bash
uv run tools/create_demo.py
uv run apps/eyeline-edit/edit_server.py .local/demo/01-recording
```

The demo creates synthetic camera/audio media locally; it contains no real recordings. See [setup](docs/setup.md) for Windows, external drives, dependencies, and LAN display mode.

## Record → cut → design → animate → finish

```mermaid
flowchart LR
  A[Script + Eyeline teleprompter] --> B[Takes + audio + JSON]
  B --> C[AI candidate cut]
  C --> D[Eyeline Edit + human review]
  D --> E[Approved WAV + transcript]
  E --> F[Design brief + Claude Design / HTML boards]
  F --> G[Animation + motion graphics]
  G --> H[Editor handoff + final video]
```

### 1. Record with the teleprompter

![Voice-following teleprompter demo](docs/media/teleprompter-demo.gif)

The recording folder keeps microphone audio, script snapshots, take metadata, captions, and a readable take report together.

![Example take files](docs/media/take-files.png)

### 2. Review the AI-assisted cut

![Adjusting clip edges against the waveform](docs/media/edge-trimming.gif)

Edit the original source intervals. Keep complete source handles available. A playback proxy covers a whole take; an assembled export never replaces the source clips. The experimental assembler writes `plan.candidate.json`, leaving your active `plan.json` alone.

### 3. Design in Claude Design or your own tool

Work from the **approved final-cut transcript**, not an earlier script. Define what each board must explain, design the boards, and review them before animation. The [design brief](templates/design-brief.md) and [Claude Design prompt](templates/claude-design-prompt.md) are editable starting points.

### 4. Add animation and motion graphics

Align graphic changes to the approved narration. Each HTML board exposes `window.seek(seconds)` so preview and export use the same deterministic state. Start with [the generic board](templates/board/index.html), customize your visual system, and render from a [timeline JSON](examples/board-timeline.json). See [design and animation](docs/design-animation.md).

### 5. Hand off to your editor

Deliver the approved cut, its WAV and transcript, source-linked plan, design assets, board renders, and timing manifest. The final editor assembles them in Resolve, Premiere, or another NLE. This release provides the files and handoff contract; it does not automate those commercial editors.

## How the system works

The following diagrams show the example workflow behind the project. Their take counts and thresholds are illustrative, not quality guarantees. The public cut generator proposes a candidate for review.

![From microphone audio and script to a take report](docs/media/take-report-architecture.png)

![From multiple takes to a draft recording plan](docs/media/edit-plan-architecture.png)

<details>
<summary>See the teleprompter layers, editing layers, and example take-selection breakdown</summary>

![Teleprompter processing layers](docs/media/teleprompter-layers.png)

![AI editing and review layers](docs/media/agent-cut-layers.png)

Editable source mapping is preserved. Redundant splits between continuous source intervals are not required. QA remains a combination of diagnostics and human listening.

![Attempts selected into one example cut](docs/media/tries-to-cut.png)

</details>

## Folder structure

```text
apps/                  Teleprompter and Eyeline Edit source
agents/                Generic role instructions and handoffs
skills/                Placeholder SKILL.md files only
config/                Workflow stages and example preferences
schemas/               Core JSON contracts
examples/              Synthetic JSON examples (no production projects)
templates/             Project tree, design brief, prompts, HTML board
tools/                 Project scaffolding, demo, render, release checks
docs/                  Setup, architecture, data formats, media and guides
```

![Example production project folder](docs/media/project-files.png)

The screenshot illustrates a real project's organization. Its project contents and backups are not bundled. Generate your own complete working folder:

```bash
python3 tools/init_project.py "/path/to/My Video"
```

## Bring your own skills

Everything in `skills/` is a **placeholder**, written for this public repository. Fill in your audience, voice, editorial rules, design tokens, animation rules, and examples. Customizing these Markdown files is prompt configuration; it does not train a model. Private channel instructions, voice fingerprints, research libraries, and proprietary skill implementations are excluded.

## Privacy and dependencies

The apps run locally. Browser speech recognition may use your browser vendor's service; QR code and font resources load from public CDNs. Whisper models and Python dependencies download on first use. Sending a transcript to an AI agent or Claude Design follows that tool's data policy. LAN display mode is opt-in and intended only for a trusted private network. See [privacy](docs/privacy.md).

**License:** code and newly authored templates are MIT. Supplied demonstration images and GIFs are documented separately in [media credits](docs/media/README.md). Third-party software and model weights retain their own licenses.
