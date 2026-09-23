# Indonesia Classification Automation Task Profile

## Registration

- Task ID: `indonesia-product-classification`
- Display name: `印尼商品运输分类`
- Task type: multi-evidence single-label classification with an operational note
- Source unit: one effective product row in an XLSX workbook
- Evidence: product image, Chinese/English name, SKU, specification, material, current route rules, and traceable historical evidence
- Output: exactly one of the nine labels plus a note when required
- Pricing and legal/customs rulings are out of scope

The platform layer follows the workspace Skill `structured-annotation-task`. This profile supplies the domain schema, labels, examples, and completion gate.

## Input record

```json
{
  "record_id": "workbook-sheet-row",
  "excel_row": 34,
  "image_id": "WPS-image-id-or-null",
  "image_ref": "portable-extracted-image-or-null",
  "sku": "401030",
  "chinese_name": "车载空调香薰",
  "english_name": "Parfum Mobil",
  "specification": "车载空调香薰",
  "material": "化工(香薰)",
  "existing_classification": "",
  "existing_note": ""
}
```

## Output record

Each proposal and final decision carries `classification`, `note`, `confidence`, `rule_id`, `basis`, `review_status`, and source provenance. `review_status=proposed` is not final.

See [example-cases.json](example-cases.json) for compact real cases extracted from completed work. These examples include field conflicts and note obligations rather than only easy keyword matches.

## Dataset splits

- `example`: records `IDN-EX-001` through `IDN-EX-006`, suitable for documentation and website display.
- `test`: records `IDN-TEST-001` through `IDN-TEST-006`, visible during implementation.
- `validation`: records `IDN-VAL-001` through `IDN-VAL-006`, reserved for acceptance checks.

For a production benchmark, retain source workbook/image provenance outside the public UI and verify that each fixture still matches the current route rules before a ruleset version bump.

## Acceptance metrics

- Schema validity and allowed-label validity: 100%.
- Required-note compliance: 100%.
- Effective-row proposal coverage: 100%.
- Image/missing-image review coverage before finalization: 100%.
- Unresolved rows before final export: zero unless explicitly accepted as pending.
- Same-image conflicts: zero.
- Unexplained same-product conflicts: zero.
- Source-column changes: zero.
- WPS image relationship/media resolution: 100% for effective image cells.

Label accuracy on the validation split is reported separately from workflow completeness. A high score cannot waive image review or artifact integrity gates.

