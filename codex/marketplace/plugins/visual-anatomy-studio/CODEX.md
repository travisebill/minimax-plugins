# Codex runtime guidance

This package contains one skill. Use the installed path below instead of relying on an unrelated global skill with the same name:

- [visual-anatomy](skills/visual-anatomy/SKILL.md): build a multi-perspective interactive HTML explainer on any topic, with media produced by tools available in the current host.

Read only the skill and references needed for the user's request. Resolve the skill's `references/` relative to its own directory.

Media providers vary by computer and session. The skill checks the live tool catalog and uses MiniMax Design MCP when present, or another compatible installed provider; no provider is a required dependency. Generated image, video and audio assets must be retrieved and placed locally before they are embedded in the page.

Use the host's available file, terminal and browser tools. Run the verification harness in `references/verify.md` before deploying, and report any browser or measurement the sandbox cannot actually perform as unverified rather than as passing.

Publishing a page creates a publicly accessible URL. Confirm before deploying unless the user already asked for a link.

