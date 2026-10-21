# Privacy and local operation

Project recordings, transcripts and scripts stay in your chosen project folder unless you deliberately share them. Neither app uploads them to a hosted editing service. Browser speech recognition can use the browser provider's remote service. The teleprompter loads QR-code JavaScript from cdnjs and fonts from Google Fonts; those third-party requests are not offline. Python packages and speech models download when first used.

A coding agent or Claude Design may receive any project content you provide to it. Review the tool's settings and policies before sharing private work. No API keys are required for these local apps, and credentials must never be committed.

Default servers bind to loopback. Optional teleprompter `--lan` allows an unauthenticated relay for a trusted secondary display; people on that network may see/control relayed session text. Do not deploy these Python servers to the public internet. GitHub hosts the source code, not an internet-facing editor.

The repository excludes live projects, audio, camera originals, caches, logs, personal machine config and private skills. Its screenshots and GIF excerpts are explicitly supplied documentation assets. Synthetic demo media is generated locally.
