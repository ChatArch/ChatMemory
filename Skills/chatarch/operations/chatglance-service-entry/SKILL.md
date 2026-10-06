---
name: chatglance-service-entry
description: Use when adding services to ChatGlance. Verify cards.
version: 0.1.0
reference:
  - local-public-service-entry-pattern: "Verify the service's local/public entry before adding a human-facing ChatGlance card"
---

# ChatGlance Service Entry

Use this skill for the standard post-service ChatArch catalog/homepage registration, or when the user explicitly asks to add a verified service to Glance/ChatGlance.

The workflow is not automatic Nginx discovery. ChatGlance uses a reviewed runtime inventory plus generated snapshots. Add one intentional service card at a time and verify it end-to-end.

## Inputs

For a service `<service>` gather:

- public URL: `https://<service>.<public-zone>/`
- local probe host: `<service>.<local-zone>`
- health URL/path, preferably a cheap local route such as `/health`
- display title and `kind`
- one-sentence human description
- short cover-summary text for the image
- optional cover image URL hosted on the managed share/image host

Do not put local probe hostnames, private IPs, API keys, cookies, or passwords on the public-facing card.

## Domain defaults and detached collection gate

Read the canonical ingress catalog and the live inventory before deriving URLs. Ensure `page.public_domain` and `page.local_domain`, or their owning typed profile defaults, are present; domain values contain no scheme, port or path. Preserve explicit per-service destinations. Run the installed `sites collect` command once into a task-owned candidate and reconcile counts/destinations before entering the live refresh queue. This isolates a missing input from an expensive scheduled pipeline or a generic collection error. Publish only through the actual supported validated pipeline and respect its lock.

For inline SVG covers, verify the image alt, decoded/load state, destination href, and visible pixels. A title rendered inside an image need not exist as DOM text. Exercise the actual open link, handling a new owned tab when appropriate; a written inventory or a locator assumption is not page acceptance.

## Procedure

1. **Verify the service first.**

   ```bash
   curl --noproxy '*' -sS -H 'Host: <service>.<local-zone>' \
     http://127.0.0.1/<health-path>
   curl -sS https://<service>.<public-zone>/<health-path>
   ```

   If the public entry is not live, stop and use `local-public-service-entry-pattern` before touching ChatGlance.

2. **Inspect the current website-services source.**

   Locate the live ChatGlance runtime home and read the reviewed inventory and generated JSON/page:

   Read `<runtime-home>/config/site-services.yml` and `<runtime-home>/data/site-services.json` with the available file tools; keep secret-bearing runtime files out of diagnostic output.

   Confirm whether the service already exists. Do not infer membership by scanning Nginx; the inventory is reviewed, not discovered.

3. **Use the self-contained inline SVG cover by default.**

   Omit `cover_url` so the installed renderer derives the title, summary and safe public destination label from the reviewed service data. Verify the visible result and retain intentional per-service URL overrides; do not hard-code a domain into artwork or display an internal probe address.

   Only when custom artwork is explicitly requested, inspect existing cards, use the `16:7` ratio, omit credentials/account/internal-address text, and publish the verified image through the managed image host. Require HTTP 200 before using that external cover.

4. **Back up and update the reviewed ChatGlance inventory.**

   Add a site entry like:

   ```yaml
   - name: <service>
     title: <Human Title>
     kind: <short category>
     description: <one sentence>
     cover_url: <public-cover-url>
     cover_summary: <short image summary>
     visual_card: true
     card_mode: visual
   ```

   Let ChatGlance derive `public_url`, `local_host`, and Uptime URL from `name` unless the service intentionally differs from the standard naming pattern.

5. **Add or update the Uptime/Gatus endpoint.**

   Add one endpoint in the same service-monitoring group used by the page:

   ```yaml
   - name: <service>
     group: <service-monitoring-group>
     url: http://127.0.0.1/<health-path>
     interval: 60s
     headers:
       Host: <service>.<local-zone>
     conditions:
       - '[CONNECTED] == true'
       - '[STATUS] < 500'
   ```

   Add a JSON-body assertion only when the health endpoint is stable and cheap, for example `- '[BODY].status == true'`.

6. **Reload monitoring through its supervisor.**

   Identify the actual supervisor first:

   ```bash
   systemctl status <gatus-service>
   systemctl show <gatus-service> --property=FragmentPath,ExecStart,MainPID,ActiveState,SubState
   ```

   Restart/reload through that supervisor; do not use `kill`/`kill -9` as a substitute for lifecycle ownership. Wait for the new endpoint to appear in the Uptime DB or UI with a latest result.

7. **Regenerate and validate the ChatGlance page.**

   Use the repository refresh script or equivalent CLI sequence:

   ```bash
   CHATGLANCE_BIN=<chatglance-bin> \
   CHATGLANCE_RUNTIME_HOME=<runtime-home> \
   CHATGLANCE_SITES_CONFIG=<runtime-home>/config/site-services.yml \
   CHATGLANCE_GATUS_DB=<gatus-db> \
   bash <chatglance-repo>/scripts/refresh-sites-page.sh

   <glance-bin> -config <runtime-home>/config/glance.yml config:validate
   systemctl --user restart <chatglance-service>
   systemctl --user is-active <chatglance-service>
   ```

8. **Verify readback.**

   Required checks:

   - generated JSON contains the service;
   - generated JSON counts increased as expected;
   - service status is `healthy` when Uptime has a successful latest result;
   - generated page YAML contains the title and cover URL;
   - live `glance.yml` still validates;
   - public Glance route still redirects/serves correctly and does not leak local hostnames;
   - the service public URL and Uptime detail URL return HTTP 200.

9. **Record the operation.**

   Update the task `progress.md` and a report with paths, backup names, generated counts, service status, and public URLs. Do not record tokens, passwords, private hostnames beyond the operator-only config path, or secret-bearing env contents.

## Do Not

- Do not auto-add every Nginx vhost.
- Do not expose local probe hostnames on the human-facing card.
- Do not publish cover images containing internal URLs, keys, account identifiers, or screenshots with secrets.
- Do not skip Uptime just because the service is currently healthy; the card should have a durable monitor link when a monitoring service exists.
- Do not replace live Glance config without `config:validate` and a timestamped backup.
