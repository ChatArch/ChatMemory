---
name: chatglance-service-entry
description: Add a verified service to the ChatGlance website-services page with cover art, Uptime/Gatus monitoring, validated config refresh, and no secret leakage.
version: 0.1.0
reference:
  - local-public-service-entry-pattern: "Verify the service's local/public entry before adding a human-facing ChatGlance card"
---

# ChatGlance Service Entry

Use this skill when a ChatArch service already has a working public entry and the user asks to add it to the current Glance/ChatGlance website showcase page.

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

   ```bash
   cat <runtime-home>/config/site-services.yml
   cat <runtime-home>/data/site-services.json
   ```

   Confirm whether the service already exists. Do not infer membership by scanning Nginx; the inventory is reviewed, not discovered.

3. **Create a cover that matches the service, not a template.**

   Check one or two existing cover images so you understand the page's visual density and card ratio. Avoid cloning the same background/composition for every card.

   Preferred cover specs:

   - wide card ratio: `16:7`, final `1280x560` PNG or equivalent;
   - include the service title and 1 short overview line in the image;
   - distinct composition based on the service's function;
   - no real URLs, tokens, account names, or internal hostnames in the image;
   - publish the final image to the managed Share/image host and verify HTTP 200.

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
