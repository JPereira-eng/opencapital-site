---
name: Always commit+push skill and agent changes
description: Every time a skill (.claude/commands/*.md) or agent file is created or modified, immediately commit and push to GitHub
type: feedback
---

Always commit and push skill/agent file changes to GitHub immediately after making them.

**Why:** Two people work on the same repo from different computers. If skills are only saved locally, the other person continues using outdated versions, causing repeated bugs and inconsistencies.

**How to apply:** After ANY edit to files in `.claude/commands/` (or future agent files), immediately:
1. `git add` the changed files
2. `git commit` with a descriptive message
3. `git push` (if rejected, stash → pull --rebase → stash pop → push)

Do this without being asked. It is a standing instruction.
