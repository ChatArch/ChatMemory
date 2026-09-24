---
name: indonesia-product-classification-workbook
description: Classify product rows in standalone Excel workbooks for Indonesia-bound shipping using product images, names, SKUs, specifications, materials, confirmed cargo rules, historical evidence, and independent review; preserve WPS DISPIMG cell images and verify the final XLSX without requiring desktop WPS Office. Use when the workbook must be filled with the nine Indonesia cargo labels and audit notes. Do not reuse the rules for pricing or another destination country without fresh confirmation.
---

# Indonesia Product Classification Workbook

Use this skill for auditable product-by-product classification, not keyword-only bulk filling.

## Required references

- Read [references/business-rules.md](references/business-rules.md) before assigning or reviewing classifications.
- Read [references/workbook-pipeline.md](references/workbook-pipeline.md) when inspecting, editing, delegating review of, or validating an XLSX workbook, especially one that uses WPS `DISPIMG` cell images.
- Read [references/automation-task-profile.md](references/automation-task-profile.md) when registering this workflow in an annotation platform, building its API/UI, or evaluating automation against the maintained examples and splits.

## Outcome

Produce a new workbook that:

- preserves the original workbook and original business columns;
- assigns every valid product row exactly one allowed classification, unless the user explicitly requests a pending-review state;
- records weak magnetism, document requirements, missing images, non-accept reasons, and image/name/material conflicts in the note column;
- can be traced back to current rules, specific reference evidence, image review, or an explicit final decision;
- preserves and verifies WPS cell-image package parts when present.

## Hard boundaries

- Treat current user-confirmed rules as higher priority than category tables and historical workbooks.
- Do not inherit a historical `不接` / non-accept result without support from a current explicit rule or fresh image review.
- Do not classify from one field alone. Cross-check image, Chinese and English names, SKU, specification, and material.
- Do not silently repair source fields. Keep the source value and write the discrepancy in the note column.
- Do not overwrite the input workbook.
- Do not make desktop WPS Office or Microsoft Excel a required dependency. Use portable XLSX/OOXML checks as the primary completion gate; a compatible desktop-app smoke test is optional unless the user explicitly requires it.
- Do not infer route prices. This skill classifies cargo types only.
- Do not reuse the rules for another destination country without new confirmation.
- Do not present the result as a legal or customs ruling; it is the confirmed operational classification for the stated route and ruleset.

## Workflow

1. Confirm the route, allowed labels, target sheet, source columns, output columns, and current rule sources.
2. Inventory the workbook: product rows, unique SKUs, formulas, images, missing images, existing labels, and package integrity. Before any model call, round-trip representative normalized records and prove that every intended source column reached the persisted task input; blank or non-standard headers are not permission to omit positional evidence.
3. Normalize historical classifications, but keep their source workbook and row for traceability. Reject blank or generic placeholder identifiers before any exact-SKU match. When a recent correction workbook overlaps a master workbook, version both evidence snapshots and use the correction workbook for the fields it actually corrects rather than blindly replacing the whole row.
4. Generate a rule-based or model proposal with rule ID, basis, note, confidence, prompt/task version, response provenance, and review status. Treat it as a proposal even when every row received a successful response.
5. Extract WPS cell images and group rows that share an image ID.
6. Review every image group and every missing-image row. When subagents are authorized and available, distribute disjoint batches and require structured results; otherwise perform the same review serially.
7. Run a separate high-risk audit for weapons/military items, drones, magnets, chemicals, batteries, medical items, pressure containers, white powders, cutting/drilling/grinding/welding products, automotive parts, hardware, lighting, and field conflicts. Re-adjudicate every master/correction disagreement from combined current evidence.
8. Merge batch corrections and explicit final overrides. Do not resolve a disagreement by repeatedly asking a model that can retrieve the exact disputed row as an example. Quarantine conflicting same-product examples from reusable gold, and use current rules, raw evidence, an independent pass without exact-row retrieval, or explicit human adjudication. After the last override, rerun same-image, same-product, note-obligation, and coverage checks.
9. Write the classification and note columns into a new workbook, then restore WPS private image parts if the authoring runtime stripped them. Prefer the bundled standard-library script so this step remains portable.
10. Verify source-column equality, classification validity, note obligations, review coverage, image relationships/hashes, archive integrity, and visual layout.

## Decision discipline

- Prefer a specific named-product rule over a broad material rule when both are current and applicable.
- Decide in this order: concrete product identity, risk-bearing structure or contents, specific route exception, then material fallback. A word such as `tool`, `metal`, `medical`, or `automotive` is not a terminal rule.
- Distinguish the product body from incidental words and accessories: a battery tester is not a battery, a plastic film is not liquid glue, and a tool made of metal is not automatically restricted hardware.
- Use confidence only to prioritize review. Confidence is not evidence and cannot waive image review.
- When two reviewers disagree, decide from the rule priority, the actual image, and the most specific supported product identity. Record the final reason.

## Completion gate

Do not declare completion until all of these are true:

- every effective row was reviewed exactly once;
- every final value is one of the nine allowed labels;
- unresolved review items are zero, or the user explicitly accepted a marked pending state;
- same-image classification conflicts are zero;
- unexplained same-product conflicts are zero;
- every non-accept row has a reason;
- required MSDS/transport appraisal, weak-magnet, missing-image, and field-conflict notes are present;
- source business columns match the original;
- output classification and notes match the final decision data;
- source-field ingestion was proven before batch proposal generation, including non-standard or blank-header columns mapped by the task contract;
- corrected-overlap rows were adjudicated from the latest combined evidence rather than whichever file ran last;
- no exact disputed record was used both as the answer-bearing retrieval example and as claimed independent verification;
- contradictory same-product examples are quarantined from reusable gold until adjudicated;
- all effective WPS image cells, including shared-formula followers, resolve to retained image package parts;
- the XLSX archive and representative visual renders pass verification.
