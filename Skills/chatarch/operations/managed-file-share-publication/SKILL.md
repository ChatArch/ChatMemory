---
name: managed-file-share-publication
description: "Use when publishing local files/dirs via ChatShare/Dufs."
version: 0.1.1
---

# Managed File-Share Publication

Use when the user asks to publish files/directories with ChatShare, or use a managed share as an image host. Reuse the existing Dufs-backed service; do not create a second file server for a publication task.

## Core rules

- Use the managed `chatshare put` command, not raw copying into the Dufs data root.
- Confirm the execution host and actual CLI contract. If the local command is missing, check standard operator locations before installing anything. If the known service runs on another approved host, use that host's existing CLI and a task-scoped transfer directory.
- Keep remote execution records in that host's Playground project; local staging is a control-plane/transfer cache. Read its workspace rules first.
- Destinations are share-relative POSIX paths. Use a concrete filename for a file; avoid leading slashes, traversal, or symlink inputs.
- Current ChatShare supports files AND native recursive directory publication. Prefer `chatshare put SOURCE_DIR DEST_PREFIX` when `put --help` confirms directory support. Manual per-file loops are only a legacy-version fallback.
- Default to no overwrite. For image hosting, a filename containing a source-content hash makes URLs immutable. Replace existing objects only with explicit authorization.
- Publish only the intended public artifacts. Exclude credentials, env/profile files, raw service responses, internal source trees and unrelated files.
- Never expose passwords, tokens, private share roots or internal service details in user replies or public examples.

## Standard flow

1. Inspect `chatshare --help`, `chatshare put --help`, `chatshare url --help`, and `chatshare tree --help` as needed. Use `chatshare --json dufs status` to confirm the existing instance. Print only necessary non-secret status fields.
2. Validate the source allowlist, regular-file count, sizes, and SHA-256 values. For a directory, preserve its relative structure.
3. Publish one file with `chatshare --json put SOURCE DESTINATION`, or a directory natively with `chatshare --json put SOURCE_DIR DEST_PREFIX`.
4. Parse and save each receipt in the task project. Verify returned path, URL, size/hash or aggregate file count according to the real command schema.
5. Read back the exact public URL anonymously. For one image, download the whole file and compare its hash, MIME type and decoded dimensions. For directories, verify the full inventory against source counts and check the intended browse/download URLs.
6. Deliver the verified bare URL immediately, with minimal useful metadata. Do this before secondary engineering, documentation, or blog changes. See `references/primary-link-before-follow-up-2026-08.md`.
7. If updating a blog, use the returned public image URL for both the image source and original-image link, then follow that publication system's PR/Preview/production gates. Keep existing unrelated downloads unchanged.

## Embedded website integrations

When adding a Share button to an existing application, first inspect and test the running share service rather than inferring its auth contract only from a client schema. Reuse ChatShare as a dependency and call `chatshare.config.merged_chatshare_environ()` for `CHATSHARE_DUFS_BASE_URL`, `CHATSHARE_DUFS_USERNAME`, and `CHATSHARE_DUFS_PASSWORD`. Do not add duplicate app-specific endpoint/token settings or invent a Bearer token interface when the real service uses account/password HTTP authentication.

Keep credentials on the backend; the browser sends only a validated generated-file identifier and receives a public URL. For an HTTP upload integration, use the existing Digest-authenticated Dufs API rather than copying directly into its data root. Verify anonymous `CHECKAUTH` rejection and configured authentication success before implementing. Bound source type/size/path, reject symlinks, use content-addressed destinations, and verify the exact public bytes after upload. Reuse existing images for browser acceptance so testing Share does not incur another generation.

### Dufs destination and conditional-write pitfalls

- With symlinks disabled, Dufs 0.46 checks that a new file's immediate parent resolves inside its root before reaching the upload handler. A missing destination directory can therefore cause an authenticated PUT to return 404.
- An anonymous GET of a nonexistent directory URL can return a virtual upload/listing page with HTTP 200. It is not proof the directory exists. Establish the fixed publication prefix through authenticated `MKCOL`, one parent at a time if necessary, and verify `PROPFIND` with `Depth: 0` returns the collection. Do not weaken the symlink/root-containment policy to fix an upload.
- Do not assume sending `If-None-Match: *` gives atomic create-only semantics: Dufs 0.46's PUT handler does not enforce this header as a verified conditional-write guard. State the actual scope of content-addressing, preflight, process-local locks and reuse; do not promise protection against unrelated concurrent writers without a proven server mechanism.
- After a known failed upload, inspect the exact target and service status before a controlled retry. Ambiguous outcomes still require readback first, never blind automatic upload retries.
- Browser acceptance must click Share, verify upload progress/error/success, actually copy/open the link, and confirm a repeat request reuses the object. Separate offline layout mocks from real endpoint evidence.

## Proxy-independent checks

For an explicit no-proxy requirement, disable environment/HTTP proxies for the read:

```bash
curl --proxy '' --noproxy '*' --fail --silent --show-error \
  --connect-timeout 10 --max-time 40 \
  --output readback.png --write-out '%{json}' "$PUBLIC_IMAGE_URL"
```

Compare the downloaded file with the original. A successful request with HTTP proxies disabled does not prove all system/VPN routing was bypassed: a fake-IP address in `198.18.0.0/15` is evidence that a DNS/TUN layer may still be involved. Use a second suitable host or an explicitly resolved real public endpoint for corroboration; do not disable the user's VPN/network configuration. Report which path was measured, not a universal speed or reachability guarantee.

## Image-hosting acceptance

- The exact returned image URL is public and anonymous, with an image MIME type and matching bytes.
- The blog's rendered image actually uses that URL and has non-zero `naturalWidth`/`naturalHeight`.
- The original-image link points at the same managed URL.
- Check actual article-body images, not hidden lazy emoji images in comment widgets.
- Verify both Preview and production after changing the blog. Upload success alone is not a completed blog update.
- Publishing an image does not authorize uploading raw SSE, secrets, or an entire internal task directory.

## Directory compatibility

Current native directory support and tree inspection are documented in `references/chatshare-native-directory-tree-2026-08.md`. On older versions that truly accept files only, enumerate regular files, append each relative source path to the destination prefix, and call `put` for each file; aggregate receipts programmatically and verify no files were dropped. Do not choose a manual loop just because an old example used one.

## Verification checklist

- Source and returned destination counts agree; file hashes/sizes match where applicable.
- Public URLs are read back, not merely constructed from memory.
- Public reachability is reported separately from local publication if verification fails.
- The primary link was delivered before optional follow-up work.
- No live service, auth configuration, or unrelated file was modified.

## References

- `references/chatshare-directory-upload-2026-08.md` — legacy per-file directory publication.
- `references/chatshare-native-directory-tree-2026-08.md` — native directory and tree support.
- `references/primary-link-before-follow-up-2026-08.md` — deliver the verified link first.
- `references/github-release-to-chatshare.md` — publishing release downloads.
