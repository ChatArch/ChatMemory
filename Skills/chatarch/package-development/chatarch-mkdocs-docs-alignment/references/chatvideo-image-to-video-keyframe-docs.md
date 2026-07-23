# ChatVideo Image-To-Video Keyframe Docs Lesson

Use this reference when a ChatArch media-generation package has correct MkDocs infrastructure but its docs do not reflect the user's actual product model.

## Session Lesson

ChatVideo's PR already had the ChatArch MkDocs mechanics: `site_url`, suffix-mode i18n, Preview Docs, Deploy Docs, Documentation metadata, and live `/dev/` checks. The missing piece was content alignment: the docs described generic video tooling instead of the user's corrected model.

Correct model for ChatVideo:

- It is image-to-video, not video chat.
- The typical input is ordered keyframe images, especially three images.
- If the provider accepts first and last frames for one segment, split a three-image storyboard into adjacent segment jobs:

```text
frame-01.png -> frame-02.png -> frame-03.png
segment-01: frame-01.png -> frame-02.png
segment-02: frame-02.png -> frame-03.png
final.mp4:  segment-01 + segment-02
```

## Review Pattern

When reviewing package docs, do not stop after confirming MkDocs mechanics. Also ask whether the docs express the corrected product model:

1. README/docs home should state the product role in the user's terms.
2. Design docs should include the core input/output model before command trees.
3. Planned commands must be labeled as design blueprints or future commands, not implied as implemented commands.
4. CLI `design` output and tests should reflect the same model as the docs.
5. PR body should record live preview URLs and validation, while formal docs avoid PR-progress narrative.

## Validation Used

- `python -m pytest -q`
- `python -m build`
- `python -m mkdocs build --strict`
- PR CI and Preview Docs checks
- HTTP 200 probes for `/dev/`, `/dev/en/`, `/dev/cli-design/`, and `/dev/en/cli-design/`
- GitHub About homepage readback

## Anti-Patterns

- Saying “video tooling” when the package is being shaped around image-to-video.
- Treating “three images” as a generic multi-image prompt instead of ordered keyframes.
- Showing `generate image` or `generate frames` as if already implemented when the PR only implements `chatvideo design`.
- Passing a docs review just because `mkdocs.yml`, workflows, and metadata are correct.
