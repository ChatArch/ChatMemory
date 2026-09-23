#!/usr/bin/env python3
"""Restore and verify WPS DISPIMG package parts without WPS Office.

Uses only the Python standard library so the skill can run on macOS, Linux,
or Windows wherever Python 3 is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import posixpath
import re
import tempfile
import zipfile
from pathlib import Path


CELL_RE = re.compile(
    r'<(?:[A-Za-z_][\w.-]*:)?c\b'
    r'(?=[^>]*\br="(?P<ref>[A-Z]{1,3}\d+)")'
    r'(?P<attrs>(?:(?!/>)[^>])*)>'
    r'(?P<body>[\s\S]*?)'
    r'</(?:[A-Za-z_][\w.-]*:)?c>'
)
IMAGE_ID_RE = re.compile(
    r'DISPIMG\((?:&quot;|")(?P<id>[^"&]+)(?:&quot;|")\s*,\s*1\)'
)
REL_RE = re.compile(r'<Relationship\b(?P<attrs>[^>]*)/?>')
ATTR_RE = re.compile(r'([A-Za-z_:][\w:.-]*)="([^"]*)"')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def worksheet_parts(names: set[str]) -> list[str]:
    return sorted(
        name
        for name in names
        if name.startswith("xl/worksheets/")
        and name.endswith(".xml")
        and "/_rels/" not in name
    )


def private_parts(names: set[str]) -> list[str]:
    return sorted(
        name
        for name in names
        if name.startswith("xl/media/")
        or name.startswith("xl/drawings/")
        or name in {"xl/cellimages.xml", "xl/_rels/cellimages.xml.rels"}
    )


def extract_image_cells(xml_text: str) -> dict[str, dict[str, object]]:
    cells: dict[str, dict[str, object]] = {}
    for match in CELL_RE.finditer(xml_text):
        cell_xml = match.group(0)
        image_match = IMAGE_ID_RE.search(cell_xml)
        if not image_match:
            continue
        explicit = bool(
            re.search(
                r'<(?:[A-Za-z_][\w.-]*:)?f\b[^>]*>[^<]*DISPIMG',
                cell_xml,
            )
        )
        cells[match.group("ref")] = {
            "image_id": image_match.group("id"),
            "explicit_formula": explicit,
            "xml": cell_xml,
        }
    return cells


def sheet_prefix(xml_text: str) -> str:
    match = re.search(r'<(?:(?P<prefix>[A-Za-z_][\w.-]*):)?worksheet\b', xml_text)
    if not match:
        raise ValueError("Unable to identify worksheet namespace prefix")
    return f'{match.group("prefix")}:' if match.group("prefix") else ""


def convert_cell_prefix(cell_xml: str, prefix: str) -> str:
    for tag in ("c", "f", "v"):
        cell_xml = re.sub(
            rf'<(/?)(?:[A-Za-z_][\w.-]*:)?{tag}\b',
            lambda match: f'<{match.group(1)}{prefix}{tag}',
            cell_xml,
        )
    return cell_xml


def replace_cell(xml_text: str, cell_ref: str, replacement: str) -> str:
    escaped = re.escape(cell_ref)
    full = re.compile(
        rf'<(?:[A-Za-z_][\w.-]*:)?c\b'
        rf'(?=[^>]*\br="{escaped}")'
        rf'(?:(?!/>)[^>])*?>[\s\S]*?</(?:[A-Za-z_][\w.-]*:)?c>'
    )
    updated, count = full.subn(replacement, xml_text, count=1)
    if count:
        return updated
    empty = re.compile(
        rf'<(?:[A-Za-z_][\w.-]*:)?c\b(?=[^>]*\br="{escaped}")[^>]*/>'
    )
    updated, count = empty.subn(replacement, xml_text, count=1)
    if not count:
        raise ValueError(f"Output worksheet is missing image cell {cell_ref}")
    return updated


def insert_before_close(xml_text: str, close_tag: str, fragment: str) -> str:
    if close_tag not in xml_text:
        raise ValueError(f"Missing closing tag {close_tag}")
    return xml_text.replace(close_tag, f"{fragment}{close_tag}", 1)


def merge_content_types(output_xml: str, source_xml: str, restored: list[str]) -> str:
    if "cellimages.xml" in " ".join(restored) and "/xl/cellimages.xml" not in output_xml:
        override = re.search(
            r'<Override\b[^>]*PartName="/xl/cellimages\.xml"[^>]*/>', source_xml
        )
        if not override:
            raise ValueError("Source workbook lacks the WPS cellimages content type")
        output_xml = insert_before_close(output_xml, "</Types>", override.group(0))

    existing_exts = {
        ext.lower()
        for ext in re.findall(r'<Default\b[^>]*Extension="([^"]+)"', output_xml)
    }
    media_exts = {
        Path(name).suffix.lower().lstrip(".")
        for name in restored
        if name.startswith("xl/media/") and Path(name).suffix
    }
    additions = []
    for ext in sorted(media_exts - existing_exts):
        content_type = mimetypes.types_map.get(f".{ext}")
        if ext in {"jpg", "jpeg"}:
            content_type = "image/jpeg"
        if not content_type:
            continue
        additions.append(
            f'<Default Extension="{ext}" ContentType="{content_type}" />'
        )
    if additions:
        output_xml = insert_before_close(output_xml, "</Types>", "".join(additions))
    return output_xml


def parse_relationships(xml_text: str) -> list[dict[str, str]]:
    return [dict(ATTR_RE.findall(match.group("attrs"))) for match in REL_RE.finditer(xml_text)]


def merge_cellimage_relationship(output_xml: str, source_xml: str) -> str:
    if any("/cellImage" in rel.get("Type", "") for rel in parse_relationships(output_xml)):
        return output_xml
    source_rel = next(
        (
            rel
            for rel in parse_relationships(source_xml)
            if "/cellImage" in rel.get("Type", "")
        ),
        None,
    )
    if not source_rel:
        raise ValueError("Source workbook lacks the WPS cell-image relationship")
    used_ids = {rel.get("Id", "") for rel in parse_relationships(output_xml)}
    rel_id = source_rel.get("Id", "rIdWpsCellImages")
    if rel_id in used_ids:
        suffix = 1
        while f"rIdWpsCellImages{suffix}" in used_ids:
            suffix += 1
        rel_id = f"rIdWpsCellImages{suffix}"
    fragment = (
        f'<Relationship Id="{rel_id}" Type="{source_rel["Type"]}" '
        f'Target="{source_rel["Target"]}" />'
    )
    return insert_before_close(output_xml, "</Relationships>", fragment)


def restore(source_path: Path, output_path: Path) -> dict[str, object]:
    with zipfile.ZipFile(source_path) as source_zip, zipfile.ZipFile(output_path) as output_zip:
        source_names = set(source_zip.namelist())
        output_names = set(output_zip.namelist())
        restored_parts = private_parts(source_names)
        required = {
            "[Content_Types].xml",
            "xl/_rels/workbook.xml.rels",
            "xl/cellimages.xml",
            "xl/_rels/cellimages.xml.rels",
        }
        missing_source = sorted(required - source_names)
        if missing_source:
            raise ValueError(f"Source workbook lacks required parts: {missing_source}")

        replacements: dict[str, bytes] = {
            name: source_zip.read(name) for name in restored_parts
        }
        restored_cells = 0
        affected_sheets = 0
        for sheet_part in worksheet_parts(source_names):
            source_xml = source_zip.read(sheet_part).decode("utf-8")
            source_cells = extract_image_cells(source_xml)
            if not source_cells:
                continue
            if sheet_part not in output_names:
                raise ValueError(f"Output workbook lacks worksheet {sheet_part}")
            output_xml = output_zip.read(sheet_part).decode("utf-8")
            prefix = sheet_prefix(output_xml)
            for cell_ref, record in source_cells.items():
                replacement = convert_cell_prefix(str(record["xml"]), prefix)
                output_xml = replace_cell(output_xml, cell_ref, replacement)
                restored_cells += 1
            replacements[sheet_part] = output_xml.encode("utf-8")
            affected_sheets += 1

        content_types = merge_content_types(
            output_zip.read("[Content_Types].xml").decode("utf-8"),
            source_zip.read("[Content_Types].xml").decode("utf-8"),
            restored_parts,
        )
        replacements["[Content_Types].xml"] = content_types.encode("utf-8")
        workbook_rels = merge_cellimage_relationship(
            output_zip.read("xl/_rels/workbook.xml.rels").decode("utf-8"),
            source_zip.read("xl/_rels/workbook.xml.rels").decode("utf-8"),
        )
        replacements["xl/_rels/workbook.xml.rels"] = workbook_rels.encode("utf-8")

        fd, temp_name = tempfile.mkstemp(
            prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
        )
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            with zipfile.ZipFile(temp_path, "w") as rebuilt:
                written: set[str] = set()
                for info in output_zip.infolist():
                    rebuilt.writestr(info, replacements.get(info.filename, output_zip.read(info)))
                    written.add(info.filename)
                for name in restored_parts:
                    if name in written:
                        continue
                    rebuilt.writestr(source_zip.getinfo(name), source_zip.read(name))
            with zipfile.ZipFile(temp_path) as check_zip:
                bad = check_zip.testzip()
                if bad:
                    raise ValueError(f"Rebuilt archive failed CRC validation at {bad}")
            os.replace(temp_path, output_path)
        finally:
            temp_path.unlink(missing_ok=True)

    return {
        "output": str(output_path),
        "affected_sheets": affected_sheets,
        "restored_image_cells": restored_cells,
        "restored_package_parts": len(restored_parts),
    }


def image_cell_map(book: zipfile.ZipFile) -> tuple[dict[str, str], int, int]:
    result: dict[str, str] = {}
    explicit = 0
    shared_followers = 0
    names = set(book.namelist())
    for part in worksheet_parts(names):
        cells = extract_image_cells(book.read(part).decode("utf-8"))
        for cell_ref, record in cells.items():
            result[f"{part}!{cell_ref}"] = str(record["image_id"])
            if record["explicit_formula"]:
                explicit += 1
            else:
                shared_followers += 1
    return result, explicit, shared_followers


def resolve_target(base_part: str, target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_part), target))


def verify(source_path: Path, output_path: Path) -> dict[str, object]:
    issues: list[dict[str, object]] = []
    with zipfile.ZipFile(source_path) as source_zip, zipfile.ZipFile(output_path) as output_zip:
        source_bad = source_zip.testzip()
        output_bad = output_zip.testzip()
        if source_bad:
            issues.append({"type": "source_crc", "part": source_bad})
        if output_bad:
            issues.append({"type": "output_crc", "part": output_bad})

        source_names = set(source_zip.namelist())
        output_names = set(output_zip.namelist())
        checked_parts = private_parts(source_names)
        missing_parts = [name for name in checked_parts if name not in output_names]
        hash_mismatches = []
        for name in checked_parts:
            if name not in output_names:
                continue
            source_hash = sha256(source_zip.read(name))
            output_hash = sha256(output_zip.read(name))
            if source_hash != output_hash:
                hash_mismatches.append(name)
        if missing_parts:
            issues.append({"type": "missing_parts", "parts": missing_parts[:50]})
        if hash_mismatches:
            issues.append({"type": "hash_mismatches", "parts": hash_mismatches[:50]})

        source_cells, source_explicit, source_shared = image_cell_map(source_zip)
        output_cells, output_explicit, output_shared = image_cell_map(output_zip)
        cell_mismatches = [
            key
            for key in sorted(set(source_cells) | set(output_cells))
            if source_cells.get(key) != output_cells.get(key)
        ]
        if cell_mismatches:
            issues.append({"type": "image_cell_mismatches", "cells": cell_mismatches[:50]})

        unresolved_ids: list[str] = []
        if "xl/cellimages.xml" in output_names and "xl/_rels/cellimages.xml.rels" in output_names:
            cellimages_xml = output_zip.read("xl/cellimages.xml").decode("utf-8")
            rels_xml = output_zip.read("xl/_rels/cellimages.xml.rels").decode("utf-8")
            rel_map = {
                rel.get("Id", ""): rel.get("Target", "")
                for rel in parse_relationships(rels_xml)
            }
            image_id_to_rel: dict[str, str] = {}
            for block in re.findall(
                r'<(?:[A-Za-z_][\w.-]*:)?cellImage\b[^>]*>([\s\S]*?)'
                r'</(?:[A-Za-z_][\w.-]*:)?cellImage>',
                cellimages_xml,
            ):
                name = re.search(r'<(?:\w+:)?cNvPr\b[^>]*\bname="([^"]+)"', block)
                rel_id = re.search(r'<(?:\w+:)?blip\b[^>]*\b(?:\w+:)?embed="([^"]+)"', block)
                if name and rel_id:
                    image_id_to_rel[name.group(1)] = rel_id.group(1)
            for image_id in sorted(set(output_cells.values())):
                rel_id = image_id_to_rel.get(image_id)
                target = rel_map.get(rel_id or "", "")
                archive_part = resolve_target("xl/cellimages.xml", target) if target else ""
                if not archive_part or archive_part not in output_names:
                    unresolved_ids.append(image_id)
        else:
            unresolved_ids = sorted(set(output_cells.values()))
        if unresolved_ids:
            issues.append({"type": "unresolved_image_ids", "ids": unresolved_ids[:50]})

        content_types_ok = (
            "[Content_Types].xml" in output_names
            and "/xl/cellimages.xml" in output_zip.read("[Content_Types].xml").decode("utf-8")
        )
        workbook_rel_ok = (
            "xl/_rels/workbook.xml.rels" in output_names
            and any(
                "/cellImage" in rel.get("Type", "")
                for rel in parse_relationships(
                    output_zip.read("xl/_rels/workbook.xml.rels").decode("utf-8")
                )
            )
        )
        if not content_types_ok:
            issues.append({"type": "missing_cellimages_content_type"})
        if not workbook_rel_ok:
            issues.append({"type": "missing_workbook_cellimage_relationship"})

    return {
        "ok": not issues,
        "source": str(source_path),
        "output": str(output_path),
        "checked_package_parts": len(checked_parts),
        "missing_parts": len(missing_parts),
        "hash_mismatches": len(hash_mismatches),
        "effective_image_cells": len(output_cells),
        "explicit_formula_cells": output_explicit,
        "shared_formula_followers": output_shared,
        "source_effective_image_cells": len(source_cells),
        "source_explicit_formula_cells": source_explicit,
        "source_shared_formula_followers": source_shared,
        "unique_image_ids": len(set(output_cells.values())),
        "unresolved_image_ids": len(unresolved_ids),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("restore", "verify"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--source", required=True, type=Path)
        sub.add_argument("--output", required=True, type=Path)
        sub.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"Source workbook not found: {args.source}")
    if not args.output.is_file():
        parser.error(f"Output workbook not found: {args.output}")

    result = restore(args.source, args.output) if args.command == "restore" else verify(args.source, args.output)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
