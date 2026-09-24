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

## File-job progress contract

Processing progress, proposal coverage, and human-review coverage are different measurements. A service should return them separately, for example:

```json
{
  "counts": {
    "total": 20,
    "proposed": 20,
    "reviewed": 2,
    "unresolved": 0,
    "remaining_review": 18
  },
  "progress": {
    "pipeline": 0.86,
    "proposal": 1.0,
    "review": 0.1
  }
}
```

- `proposal` answers how many effective records have an automation proposal.
- `review` answers how many effective records have a final accepted or corrected human decision.
- `remaining_review` is the number still lacking a final human decision; unresolved records remain unfinished.
- `pipeline` may summarize execution stages, but the UI must not present it as annotation completion.
- A partial-review page must show the numerator, denominator, percentage, unresolved count, and remaining count. Final validation/export remains unavailable until the task completion gate passes.

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
- Split by the strongest shared identity available, such as exact SKU, image hash, or normalized product family, so near duplicates cannot cross from train/examples into acceptance evaluation.
- Freeze and hash the acceptance set before its first evaluated run. Cases inspected to change the current prompt, rules, or retrieval library move to regression history in the next version rather than remaining “unseen.”
- Quarantine contradictory same-identity labels from gold until an explicit adjudication records the chosen label and reason.

## Ingestion preflight

Before a bulk proposal job can leave normalization:

- read representative persisted records back through the production API or store boundary;
- compare all required task fields and evidence states to source artifacts, including positional columns with blank or non-standard headers;
- record field-population and evidence-resolution counts;
- fail closed when an intended source column is unexpectedly empty or evidence resolution materially differs from the source inventory.

Proposals produced before a failed evidence preflight are invalid for final decisions and ground truth, even if their API calls succeeded.

## Shared UI contract

The first screen is the working annotation console, not a marketing page. It should include task selection, dataset upload, processing status, record review, evidence preview, filters, label controls, notes, unresolved queue, aggregate metrics, and export. Shared UI text should describe generic annotation concepts; task-specific labels and help come from the selected manifest.

Use a quiet operational layout with clear hierarchy, restrained color, compact tables, keyboard-friendly review, and a detail pane for evidence. A task may supply label colors, but the platform must not become a one-color theme or hard-code one domain's visual language.

When a file task is active, show automation progress and human-review progress in separately labeled bars or counters. Do not let a completed proposal stage visually imply completed annotation review.
