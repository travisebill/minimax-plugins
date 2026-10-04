# Codex plugin sources

These instructions apply to `codex/`. The parent repository's MiniMax runtime rules apply only to its top-level `plugins/` directory.

- Author source in `marketplace/plugins/<name>/`; read the target package's `CODEX.md` and relevant skill before changing behavior.
- Keep `plugin.json` (Agent Plugins 1.0) and `.codex-plugin/plugin.json` synchronized in identity, version and UI metadata. Preserve source attribution in `UPSTREAM.json`.
- The repository root `.agents/plugins/marketplace.json` resolves paths from the repository root. The copy under `codex/marketplace/.agents/plugins/marketplace.json` resolves paths from `codex/marketplace`. Keep their plugin names and policies aligned.
- Use the installed Plugin Creator and Skill Creator guidance when changing packages. Run `python3 scripts/package_plugins.py` (PyYAML required) to validate and export. Use Codex CLI for authorized installs; never edit its cache directly.
- `scripts/verify_host.py` checks actual installed plugin metadata without a model request. Report missing runtime or external generation evidence honestly.
- Keep logs, credentials, local environment files and absolute machine paths out of commits and archives. Human documentation is Traditional Chinese; runtime guidance and machine records may be English.
- Changes to the Codex packages do not require modifying or bumping the MiniMax packages. Preserve their content unless separately requested.
