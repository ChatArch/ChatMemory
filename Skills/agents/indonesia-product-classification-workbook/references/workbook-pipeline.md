# Workbook, Image Review, and Verification Pipeline

Read this reference when working on an actual XLSX file. Adapt paths, sheets, columns, and counts to the current workbook; the validated case numbers at the end are benchmarks, not universal constants.

## 1. Establish a task record

Follow the host workspace convention. Record at least:

- input workbook and reference sources;
- route scope and allowed labels;
- target sheet and source/output columns;
- explicit business rules and conflict priority;
- whether prices are out of scope;
- acceptance criteria and output path.

Keep the original workbook read-only and write intermediate data inside the task/project area.

## 2. Discover the workbook instead of assuming its shape

Inspect:

- sheet names and used ranges;
- row count and header row;
- Chinese name, English name, image, SKU, specification, and material columns;
- existing classification and note columns, if any;
- unique and duplicate SKUs;
- formulas, especially WPS `DISPIMG`;
- image formula count, unique image ID count, and blank-image rows;
- archive integrity with a standard ZIP library or an available platform utility. Do not require the POSIX `unzip` command.

Do not assume the business sheet is `sheet1.xml`. Resolve the sheet relationship when the workbook layout differs.

Create a normalized target record for each product, retaining the original Excel row number:

```json
{
  "row": 2,
  "chineseName": "<chinese-product-name>",
  "englishName": "<english-product-name>",
  "imageFormula": "=DISPIMG(\"ID_EXAMPLE\",1)",
  "imageId": "ID_EXAMPLE",
  "sku": "<sku>",
  "specification": "<specification>",
  "material": "<material>"
}
```

## 3. Build traceable reference evidence

Normalize label variants from recent workbooks into the nine allowed labels while retaining:

- source workbook;
- source row;
- source SKU/name/material/use;
- source classification and note.

Match in this order: exact SKU, exact normalized product identity, then carefully reviewed same-use/same-material similarity. Before exact-SKU matching, exclude blank and generic placeholder values such as `组合`, `以后增加`, `待定`, and similar non-identifiers; otherwise unrelated rows can inherit one another's history. Do not let broad substring matches override the product body.

Audit conflicts separately. Historical non-accept matches should be listed for review, not applied automatically.

## 4. Extract WPS cell images

WPS cell images commonly use:

```text
worksheet cell formula DISPIMG(image-id)
  -> xl/cellimages.xml
  -> xl/_rels/cellimages.xml.rels
  -> xl/media/<image>
```

Build a mapping from image ID to the extracted local image and original archive part. Fail or flag when an ID cannot be resolved. Group rows by shared image ID so identical images receive one visual decision.

Do not count only formula tags that contain literal `DISPIMG` text. WPS may store one leader formula and follower cells as `<f t="shared" .../>`, with each follower's effective `DISPIMG` expression cached in `<v>`. Count effective image cells from the cell formula or cached value, preserve the original cells, and resolve every extracted image ID.

For missing-image rows, review all text fields and require a missing-image note. Do not invent visual details.

## 5. Generate proposals, not final answers

Each initial proposal should include:

- classification;
- note;
- confidence;
- rule ID;
- rule basis;
- review status.

Apply explicit user rules first, then current specific category rules, then historical evidence, then conservative fallback. Confidence only determines review order.

In a service, proposal generation completion and annotation completion are separate counters. Persist and expose `total`, `proposed`, `reviewed`, `unresolved`, and `remaining_review`; report proposal and review percentages independently. If only 10% of rows were human-reviewed, call the file 10% reviewed even when every row already has a proposal.

Guard against substring and subject errors. Validated failures included:

- `pink` or `shrink` falsely matching `ink`;
- oil/fuel pump names being treated as chemical liquids;
- battery testers, battery boards, storage boxes, motors, clips, chargers, and related accessories being treated as battery bodies;
- `胶` inside `橡胶`, or in the name of an applicator, tube, or nozzle, being treated as shipped glue;
- spray nozzles, sprayer booms, and spray tools being treated as pressure containers, while an innocuous text label can still hide an actual aerosol or pressure can in the image;
- product names containing `car`, `face-mask`, `tool`, `wire`, or `cup cover` overriding the image body;
- material-only decisions that ignored a tool, automotive part, medical use, or embedded magnet.

## 6. Create visual-review batches

Create one review item per unique image ID and one item per missing-image row. A useful batching strategy is:

1. sort image groups by the minimum proposal confidence;
2. keep all rows sharing an image in the same group;
3. create contact sheets with readable row numbers and proposal labels;
4. include the source JSON beside the contact sheet.

When subagent delegation is authorized by the user or active instructions, wait until the schema, rules, normalization, and proposal format are stable, then assign disjoint image groups to independent reviewers. Otherwise use the same batch protocol serially. Keep one merger and one workbook writer; do not let multiple reviewers edit the workbook.

Each reviewer must inspect every assigned group and return structured data:

```json
{
  "batchId": "01",
  "reviewedImageGroupCount": 180,
  "reviewedRows": 182,
  "corrections": [
    {
      "rows": [55],
      "classification": "敏感类",
      "note": "optional replacement note",
      "reason": "why the proposal is wrong"
    }
  ],
  "dataQualityNotes": [
    {
      "rows": [73],
      "note": "image shows textile straps but material lists only plastic"
    }
  ],
  "unresolved": []
}
```

Validate that:

- counts match the batch manifest;
- every referenced row belongs to the batch;
- labels are legal;
- rows are not duplicated across corrections;
- corrections actually change the proposal or its note;
- every image group and missing-image row is covered.

## 7. Run a high-risk audit

Independently rescan product names, SKUs, materials, notes, and images for:

- military, camouflage, gun, sight, weapon, drone, and remote-aircraft terms;
- magnets and magnetic accessories;
- needles, dental, ostomy, postoperative, emergency, rehabilitation, and other medical terms;
- glue, resin, ink, paint, cleaner, polish, powder, alcohol, iodine, batteries, and pressure containers;
- automotive, hardware, tools, lighting, and textile mixtures;
- image/name/material conflicts.

The audit should catch dangerous false negatives and broad-rule false positives. Record final overrides with row, classification, optional note, and reason.

## 8. Merge with full coverage guarantees

Start from the proposal set, then apply:

1. batch corrections;
2. batch data-quality notes;
3. explicit final audit overrides.

The merger should fail when:

- a batch is missing;
- a reviewer reports unresolved items;
- review counts differ from the manifest;
- a product row is missing or reviewed by more than one batch;
- a final label is invalid.

Create:

- final row decisions;
- a change/audit log;
- a summary of label counts, reviewed rows, image-reviewed rows, missing-image rows, and note rows.

After all batch corrections and final overrides, rerun the full consistency suite. Any later correction must trigger it again. Before authoring the workbook, assert:

- no shared image ID has conflicting classifications;
- same-name differences are either resolved or explained by image/material/use;
- every non-accept row has a reason;
- every accepted chemical that requires documents has the required note;
- every embedded magnet has `弱磁`;
- every missing-image row has a note.

Do not trigger chemical-document notes from the final A/B label alone. Re-evaluate the source evidence and require those documents only when the actual product contains an applicable chemical; category-driven non-chemical A/B items do not inherit the obligation.

## 9. Author the output workbook

Use a spreadsheet-capable runtime that preserves formatting and formulas. Follow the active spreadsheet skill's operation marker and authoring requirements when present.

Recommended behavior:

- import the original workbook;
- copy an adjacent source-column style into the new classification and note columns;
- write fixed headers;
- write final classification and note values in one range operation;
- add list validation for the nine labels;
- set readable widths, alignment, and note wrapping;
- compare untouched source columns before export;
- compare the image column by formula, not evaluated value;
- export to a new path.

Some spreadsheet runtimes evaluate unsupported `DISPIMG` formulas as `#NAME?`. Do not treat the evaluated image-cell value as a source-data change. Protect the original formula and OOXML package instead.

## 10. Restore WPS private image parts without desktop WPS

Generic XLSX writers may keep formula text while dropping WPS image package parts. If package comparison shows this happened, rebuild the exported archive by restoring from the source workbook:

- `xl/media/*`;
- `xl/drawings/*`;
- `xl/cellimages.xml`;
- `xl/_rels/cellimages.xml.rels`;
- the original image-formula cells in the target worksheet XML;
- the WPS cell-image content type;
- the workbook relationship to `/xl/cellimages.xml`.

Use a temporary directory, build a new archive, and atomically replace only the new output file. Never modify the source workbook. Do not save the restored output through software that removes unknown OOXML extensions before verification.

Prefer the bundled cross-platform script, which uses only the Python standard library and does not require WPS Office, Excel, `zip`, or `unzip`:

```bash
python scripts/wps_cell_images.py restore --source source.xlsx --output output.xlsx
python scripts/wps_cell_images.py verify --source source.xlsx --output output.xlsx
```

The restore command is intentionally source-to-output: it copies the source-owned WPS media and private OOXML parts, restores effective image cells including shared-formula followers, merges the required content type and workbook relationship, validates the rebuilt ZIP, and atomically replaces only the output. The verify command compares package-part hashes, effective cell-to-image mappings, shared-formula counts, relationships, media resolution, and archive CRCs without opening a desktop office application.

## 11. Verify the final artifact

Perform all of the following:

### Semantic checks

- output row count and headers;
- source-column equality;
- image-formula equality;
- final classification/note equality to decision data;
- allowed-label membership;
- classification counts and note count.

### Package checks

- ZIP integrity;
- required media, drawings, cell-image XML, and relationships present;
- relevant package-part hashes equal the source;
- expected image formula count and unique ID count;
- effective image-cell count, distinguishing literal formulas from shared-formula followers when present;
- every formula ID resolves through cell-image relationships to a retained media part.

### Visual checks

Render or inspect the top, middle, and bottom of the business sheet plus any reserved cell-image sheet. Confirm new columns, widths, wrapping, and source layout. Review the extracted source images or contact sheets for product identity. A generic renderer may show `#NAME?` for valid WPS `DISPIMG` cells; treat that as an expected renderer limitation only after the package checks pass.

Desktop WPS Office is an optional smoke test, not a completion dependency. When a compatible desktop app is already available, spot-check representative images for added confidence. When it is unavailable, complete the task from semantic checks, portable OOXML/package verification, extracted-image review, and generic layout renders, and state that the optional client-rendering test was not performed. If the user explicitly requires proof of rendering in a particular desktop app, that app or an equivalent compatible environment is required for that extra acceptance criterion.

Only formula errors outside expected WPS `DISPIMG` evaluation should count as new formula failures.

## 12. Validated case benchmark

One completed workbook validated this process with:

- 1,047 product rows and unique SKUs;
- 1,044 image-formula rows;
- 3 missing-image rows;
- 1,033 unique image IDs;
- 1,036 image/missing-image review groups across six batches;
- zero unresolved rows;
- zero source-column mismatches;
- zero final decision mismatches;
- 1,017 WPS image-related package parts with zero missing parts and zero hash mismatches;
- a valid XLSX ZIP archive.

Use these figures only to reproduce that exact case. A new workbook must discover and verify its own counts.
