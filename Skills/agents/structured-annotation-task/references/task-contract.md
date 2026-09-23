# Annotation Task Contract

## Registration manifest

Each task profile should provide:

```json
{
  "task_id": "stable-kebab-case-id",
  "version": "semver-or-date-version",
  "display_name": "Human-facing name",
  "description": "What is being annotated and why",
  "input_schema": {},
  "output_schema": {},
  "label_set": [],
  "evidence_types": [],
  "ruleset_refs": [],
  "example_set": "relative/path.json",
  "test_set": "relative/path.json",
  "validation_set": "relative/path.json",
  "completion_gate": []
}
```

The manifest contains no credentials and no machine-specific absolute paths.

## Record lifecycle

Use explicit states:

```text
uploaded -> normalized -> proposed -> in_review -> reviewed -> validated -> exported
                                      \-> unresolved
```

- `proposed` means automation produced a candidate label and note.
- `reviewed` means the required evidence was checked and a reviewer accepted or corrected the proposal.
- `validated` means dataset-level coverage, consistency, note obligations, and artifact checks passed.
- `exported` means a new deliverable was written without mutating the source.

Track job state separately as `queued`, `running`, `succeeded`, or `failed`.

## Output record

```json
{
  "record_id": "source-stable-id",
  "proposal": {
    "label": "label-id",
    "note": "optional operational note",
    "confidence": "high|medium|low",
    "rule_id": "task-rule-id",
    "basis": "evidence-based reason"
  },
  "review": {
    "status": "pending|accepted|corrected|unresolved",
    "final_label": null,
    "final_note": null,
    "reason": null,
    "reviewer": null,
    "reviewed_at": null
  }
}
```

## Dataset design

- Example set: small, readable cases shown in docs and the product UI.
- Test set: deterministic cases available during development; cover schema, every label when practical, edge conditions, and note obligations.
- Validation set: separately identified cases used for acceptance metrics and regression checks.
- Keep source provenance and expected-decision provenance for every fixture.
- Include counterexamples where keyword-only classification would fail.

## Shared UI contract

The first screen is the working annotation console, not a marketing page. It should include task selection, dataset upload, processing status, record review, evidence preview, filters, label controls, notes, unresolved queue, aggregate metrics, and export. Shared UI text should describe generic annotation concepts; task-specific labels and help come from the selected manifest.

Use a quiet operational layout with clear hierarchy, restrained color, compact tables, keyboard-friendly review, and a detail pane for evidence. A task may supply label colors, but the platform must not become a one-color theme or hard-code one domain's visual language.

