# Codex runtime guidance

## Package routing

Use the installed files below, even when older global skills have matching names. A sibling skill handoff means reading its file with the available file tool. It does not require MiniMax's `skill` tool or a separate agent.

| Request | Bundled skill |
| --- | --- |
| Whole workflow or resume | [yt-focus-music-pipeline](skills/yt-focus-music-pipeline/SKILL.md) |
| Release and long-form assembly planning | [three-kingdoms-focus-music](skills/three-kingdoms-focus-music/SKILL.md) |
| Character-led project, covers and chapter images | [three-kingdoms-video-project](skills/three-kingdoms-video-project/SKILL.md) |
| Instrumental caption | [music3-instrumental-prompts](skills/music3-instrumental-prompts/SKILL.md) |
| Prompt, technical, listening or continuity review | [three-kingdoms-music-review](skills/three-kingdoms-music-review/SKILL.md) |
| Character vocal single and storyboards | [three-kingdoms-vocal-single](skills/three-kingdoms-vocal-single/SKILL.md) |
| YouTube metadata and policy checks | [yt-publish-strategy](skills/yt-publish-strategy/SKILL.md) |

Resolve a skill's `references/`, `templates/` and `scripts/` relative to that skill directory. Keep generated project files in the user's workspace, outside the installed plugin. `SKILL.cn.md` and `meta.yaml` are retained upstream companion material; `SKILL.md` is the executable workflow entrypoint.

## Approval and evidence

Read current project specifications, candidate manifests and approval records before resuming. Explicit user instructions and project-specific approved decisions take precedence over generic workflow defaults.

Every newly drafted or materially revised music prompt must pass the bundled music review on the exact final payload before it is presented for approval or submitted. Save a versioned report under the project's `music-review/`; any later payload edit requires another review. Keep each provider payload standalone, with track planning in separate continuity records.

`prompt 已確認` authorizes immediate generation for the confirmed payload version, provider, settings and declared candidate count. Reuse that authorization without another execution confirmation. Explicit authorization to revise and then generate also permits execution after the revised payload has been reviewed. Candidate selection, assembly, cover selection and publication retain their own approval scopes. Preserve all candidates and original provider files.

Measure audio with the bundled helper using Python 3.11 or newer, `ffmpeg` and `ffprobe`. Check these executables only when technical audio work is needed. Use an absolute script path and a new report path. A measurement, waveform or embedded player provides no auditory perception: listening remains `not-assessed` without actual audio-native or human evidence.

## Available capabilities and external dependencies

This is a skills package with a local measurement helper; it supplies no MCP server, provider credentials, music/video endpoint or YouTube upload connector. Discover the host's actual tools before each external operation. Use the selected provider and the user's authorized account. If the required capability is missing, finish the approved local artifacts and give an exact handoff instead of claiming generation or publication occurred.

For image work use the host's available image generation/editing tool and approved references. For external music/video generation preserve the approved payload and record the actual response, task or file as evidence. A generated file may arrive through an authorized tool or from the user; verify its provenance and decode before intake.

`music-caption-rewriter` is an external prerequisite for the MiniMax workflow that requires it. Discover the installed skill through Codex's skill catalog and read that actual file. The existing `three-kingdoms-video-project` section describes how to install it if missing. This package does not silently substitute its instrumental skill for that prerequisite. Lyria workflows and unrelated planning do not require it.

Provider limits, access policies, prices, model IDs and YouTube rules in the upstream files are dated reference material. Verify consequential current claims against official provider/YouTube documentation before advice or execution, record the checked date and selected interface, and distinguish hosted APIs, model weights and website fields. Upstream channel comparisons are historical snapshots, not current search rankings or guaranteed outcomes.
