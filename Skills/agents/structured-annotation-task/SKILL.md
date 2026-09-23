---
name: structured-annotation-task
description: Formalize, implement, or review a reusable annotation task with versioned input/output schemas, examples, test and validation splits, execution states, review gates, and a task-neutral UI. Use when turning a one-off labeling workflow into a registered automated annotation task. Do not embed one domain's labels or rules into the platform layer.
---

# Structured Annotation Task

Build the platform and the task definition as separate layers. The platform owns upload, task lifecycle, evidence display, reviewer actions, audit history, exports, and evaluation. A task profile owns its fields, labels, rules, examples, metrics, and completion gate.

## Required reference

Read [references/task-contract.md](references/task-contract.md) when defining a task profile, API, dataset split, or annotation UI.

## Workflow

1. Assign a stable task ID and version. Record the task owner, purpose, exclusions, and source-of-truth rules.
2. Define machine-readable input and output schemas. Keep source fields immutable and put derived values in explicit proposal/final-decision fields.
3. Provide representative examples, including ordinary cases, high-risk boundaries, missing evidence, field conflicts, and note obligations.
4. Split fixtures into visible tests for development and a separate validation set for acceptance. Do not tune against validation failures without versioning the task or split.
5. Run automation as a proposal stage. Require the task profile's review and completion gate before marking annotations final.
6. Present evidence, proposal, confidence, rule basis, reviewer decision, notes, and unresolved status in the UI. Avoid domain-specific labels in shared components.
7. Preserve an audit trail from source record through proposal, review, override, export, and evaluation.

## Completion boundary

A processing job may be complete while annotation review is not. Report these states separately. Never map a successful model/API call directly to `final` unless the task profile explicitly permits fully automatic acceptance and defines measurable gates for it.

