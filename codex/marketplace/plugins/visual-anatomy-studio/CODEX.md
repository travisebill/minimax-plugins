# Codex runtime guidance

This package contains one skill. Use the installed path below instead of relying on an unrelated global skill with the same name:

- [visual-anatomy](skills/visual-anatomy/SKILL.md): build a multi-perspective interactive HTML explainer on any topic, with generated illustrations, H3 video, clickable hotspots, drag comparators and a deployed URL.

Read only the skill and references needed for the user's request. Resolve the skill's `references/` relative to its own directory.

Use the host's available file, terminal and browser tools. Run the verification harness in `references/verify.md` before deploying, and report any browser or measurement the sandbox cannot actually perform as unverified rather than as passing.

Publishing a page creates a publicly accessible URL. Confirm before deploying unless the user already asked for a link.
