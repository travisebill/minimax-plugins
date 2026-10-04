# Codex runtime guidance

This package contains two skills. Use the installed paths below instead of relying on an unrelated global skill with the same name:

- [learning-mechanics](skills/learning-mechanics/SKILL.md): select, implement and validate the learning mechanic.
- [learning-game-feel](skills/learning-game-feel/SKILL.md): implement and measure feedback, accessibility and responsiveness.

Read only the skill and references needed for the user's request. A mention of a sibling skill means read that file; it does not require a MiniMax `skill` tool or a separate agent. Resolve each skill's `references/` relative to its own directory.

Use the host's available file, terminal and browser tools. Inspect the project's framework, progress schema and existing tests before editing. Read the available browser tool documentation before using it; report unavailable browser or performance measurements as unverified.

`progressive-learning-site` and `game-studio` are optional companion capabilities, not bundled dependencies. Use them only when present and appropriate. Otherwise follow the project's existing curriculum and rendering architecture; this plugin can still implement its own mechanics and feedback scope. Expanding into a complete course or a different rendering engine requires that actual user scope.

Preserve the project's language and design conventions. Human deliverables default to Traditional Chinese. Report measured results separately from design targets; in particular, do not invent learner pass rates from a developer smoke test.
