Read AGENTS.md, then docs/workflow.md. Role instructions are in agents/. Customize skills/ placeholders before using them for creative decisions. Work on a project under .local/ or a separate storage location; do not publish its files.

@AGENTS.md

## Shorts (Reels/TikTok) — монтаж для автора
Скилл `shorts` (+ профили `lawyer`, `autoservice`). В новой сессии сначала: `bash tools/shorts/setup.sh`.
Рабочие файлы проекта — в `.local/<проект>/` (src/, words.json, faces.json, sfx/, timeline.py), примеры таймлайнов — `tools/shorts/examples/`.
Порядок: распознать речь → раскадровка скриншотами → правки → `render.py --final` и отдать файлом.

