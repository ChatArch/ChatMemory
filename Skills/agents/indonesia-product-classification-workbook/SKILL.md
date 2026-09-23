---
name: indonesia-product-classification-workbook
description: Classify product rows in standalone Excel workbooks for Indonesia-bound shipping using product images, names, SKUs, specifications, materials, confirmed cargo rules, historical evidence, and independent review; preserve WPS DISPIMG cell images and verify the final XLSX. Use when the workbook must be filled with the nine Indonesia cargo labels and audit notes. Do not reuse the rules for pricing or another destination country without fresh confirmation.
---

# Indonesia Product Classification Workbook

Use this skill for auditable product-by-product classification, not keyword-only bulk filling.

## Required references

- Read [references/business-rules.md](references/business-rules.md) before assigning or reviewing classifications.
- Read [references/workbook-pipeline.md](references/workbook-pipeline.md) when inspecting, editing, delegating review of, or validating an XLSX workbook, especially one that uses WPS `DISPIMG` cell images.

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
- Do not infer route prices. This skill classifies cargo types only.
- Do not reuse the rules for another destination country without new confirmation.
- Do not present the result as a legal or customs ruling; it is the confirmed operational classification for the stated route and ruleset.

## Workflow

1. Confirm the route, allowed labels, target sheet, source columns, output columns, and current rule sources.
2. Inventory the workbook: product rows, unique SKUs, formulas, images, missing images, existing labels, and package integrity.
3. Normalize historical classifications, but keep their source workbook and row for traceability.
4. Generate a rule-based proposal with rule ID, basis, note, confidence, and review status.
5. Extract WPS cell images and group rows that share an image ID.
6. Review every image group and every missing-image row. When subagents are authorized and available, distribute disjoint batches and require structured results; otherwise perform the same review serially.
7. Run a separate high-risk audit for weapons/military items, drones, magnets, chemicals, batteries, medical items, pressure containers, white powders, tools, automotive parts, hardware, lighting, and field conflicts.
8. Merge batch corrections and explicit final overrides. Resolve every conflict; do not hide unresolved rows in a broad default category.
9. Write the classification and note columns into a new workbook, then restore WPS private image parts if the authoring runtime stripped them.
10. Verify source-column equality, classification validity, note obligations, review coverage, image relationships/hashes, archive integrity, and visual layout.

## Decision discipline

- Prefer a specific named-product rule over a broad material rule when both are current and applicable.
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
- all WPS image formulas resolve to retained image package parts;
- the XLSX archive and representative visual renders pass verification.
