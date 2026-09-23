# Indonesia Cargo Classification Rules

Read this reference whenever assigning or reviewing classifications. These rules represent the validated operating policy behind the skill; re-confirm them when the destination, route owner, or category table changes.

## Scope and labels

The validated workflow used one shared classification policy for multiple China warehouses shipping to Indonesia. It did not calculate prices.

The classification value must be exactly one of:

```text
普货
商检货
敏感类
A类特敏
B类特敏
纺织类
慢线半纺织
慢线纺织
不接
```

Use the note field for conditions and evidence; do not invent label variants such as `敏感`, `商检`, or `待定` unless the user changes the schema.

## Evidence priority

When evidence conflicts, apply this order:

1. current user-confirmed rules for this route;
2. the latest Indonesia category table, except an explicitly disclaimed historical non-accept section;
3. recent confirmed classification workbooks;
4. exact SKU, exact product, then same-use/same-material historical evidence;
5. similar-product inference, which requires explicit review rather than silent certainty.

A current specific product rule normally beats a broad material fallback. A current explicit user rule beats both.

## Hardware, tools, keys, and automotive products

- General metal hardware and restricted stainless-steel hardware are `敏感类`. Typical examples include rails, hinges, racks, brackets, generic metal storage hardware, and coated metal wire.
- A usable hand tool, tool attachment, or tool consumable is normally `普货`, even when metal.
- A clearly identified automotive, motorcycle, or vehicle functional part is normally `商检货`.
- Automotive lights are a confirmed exception and are `普货`.
- A metal key is `商检货`.
- A key cover, key ring, or T-handle removal tool is not a metal key; classify the actual product.
- An automotive seat cushion follows the specific category-table rule `敏感类`, rather than the broad automotive-parts fallback.

Use the image to distinguish a functional part, a repair tool, generic hardware, and a decorative accessory.

## Lighting

- Automotive lights: `普货`.
- Flashlights: `普货`.
- Portable, hand-carried solar lights: `普货`.
- Plug-in lights: `敏感类`.
- Other decorative lighting: `敏感类`.
- A switch, controller, bracket, or wiring harness is classified as its actual electrical/automotive component, not as the lamp body.

## Magnets

- Strong magnets, pure magnets, and standalone magnet products: `不接`.
- A product that merely contains a magnet is classified by its product body and must include the note `弱磁`.
- Confirm magnetic strength when the source material omits the magnet or the image does not establish whether the item is standalone.
- Do not treat every occurrence of the word `magnetic` as a physical magnet; it may be part of an instrument name.

## Non-accept boundaries

The current explicit non-accept set includes:

- military products;
- drones and drone equipment or parts;
- realistic toy guns, related toys, and gun accessories;
- camouflage products;
- highly sensitive, invasive, or otherwise explicitly rejected medical devices or postoperative medical items;
- strong magnets and standalone magnets;
- pressure containers;
- white powder products;
- confirmed dangerous goods.

Images control when a generic product name hides a prohibited item, such as a model set that is actually a firearm optic or an unspecified repair cable that is actually a drone gimbal cable.

Do not copy historical non-accept values merely because the old workbook contains them. Re-establish the current reason.

## Medical, gloves, and protective products

- Pulse oximeters, blood-pressure monitors, and hearing aids: `敏感类`.
- Rubber, TPE, nitrile, and plastic gloves: `普货`.
- Gloves and protective products with meaningful textile construction use a slow-line textile category.
- Confirmed slow-line examples include aramid gloves, leather gloves, lead-rubber collars, flame-retardant caps, lead-rubber textile aprons, knee ice packs, fiberglass fire blankets, and lead-rubber protective garments.
- Orthoses and posture supports are classified from exact use, structure, image, and material. A textile brace with hard support is usually `慢线半纺织`; a sensitive electronic or invasive device may be `敏感类` or `不接`.
- The piano hand/posture corrector is an explicitly confirmed `普货` example.
- Microneedle rollers, dental instrument trays, ostomy bags, anti-choking suction devices, and postoperative breast prostheses were treated as `不接` in the validated case because their specific medical use crossed the confirmed sensitivity boundary.

## Glue, batteries, and chemicals

- Ordinary glue: `A类特敏`.
- Cosmetic eyelash glue: `B类特敏`.
- Battery bodies and products governed by the explicit battery rule: `敏感类`.
- Other chemicals are classified by the exact product. Accepted chemical products require the note:

  `需提供MSDS和运输鉴定报告，确认非危险品后可接`

- Confirmed dangerous chemicals are `不接`.
- Alcohol- or iodine-filled swabs are not dry cotton swabs; classify the chemical liquid and require documentation.
- A solid protective film, adhesive strip, silicone article, or tape is not automatically liquid glue.
- A pump, valve, or hose whose name contains oil/fuel is not necessarily shipping with liquid. Note `不含液体` when the image and declaration support that distinction.

Where a current route table names power banks or another battery-containing finished product differently from the explicit battery rule, surface the conflict and resolve it by the evidence priority rather than choosing silently.

## Textiles

Use the exact route table where it provides a named product. As a fallback:

- `纺织类`: ordinary clothing where the route policy assigns the standard textile line.
- `慢线半纺织`: mixed products with meaningful textile components plus plastic, metal, foam, rubber, or other structures; common examples include textile straps, braces, masks, gloves, bath caps, and mixed fabric accessories.
- `慢线纺织`: predominantly textile slow-line goods such as certain nets, carpets, curtains, or large textile bodies.
- `B类特敏`: confirmed intimate apparel, underwear, shapewear, nipple covers, cosmetics, personal-care, or other named B-class products.

Do not classify a wig, baseball cap, plastic mask, silicone face support, tool consumable, or plastic toy by a generic textile material token when a more specific current product rule exists.

## Notes

Write notes when any of these applies:

- `弱磁` for embedded weak magnets;
- MSDS and transport appraisal requirement for accepted chemicals/glues;
- `含电池` when battery content is not obvious from the source fields;
- the precise reason for `不接`;
- missing product image;
- `确认品名`, `确认材质`, or a concrete conflict between image, name, specification, and material;
- a condition that would change the result, such as “if the set contains a realistic gun accessory, do not accept.”

Do not retain an obsolete note after changing the classification. For example, when a supposed glue is confirmed to be a solid protective film, remove the chemical-document note and explain the corrected product identity instead.
