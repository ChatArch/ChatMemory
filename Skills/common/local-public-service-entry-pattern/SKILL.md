---
name: local-public-service-entry-pattern
description: Shared workflow for exposing a machine-local service through local nginx plus an automatic public entry, without per-service DNS or certificate drift.
version: 0.1.0
---

# Local/Public Service Entry Pattern

Use this skill when a service is already running on a machine and needs to be exposed through a domain name and public HTTPS access.

This is the shareable service-exposure pattern. Keep machine names, concrete IPs, private keys, DNS provider tokens, and FRP tokens in the machine-local skill copy, not here.

## Skill Boundary

This skill starts after the application service is running. It covers only the exposure step:

- give the service a local nginx hostname;
- rely on wildcard DNS instead of adding per-service DNS records;
- rely on a shared wildcard certificate instead of creating per-service certificates;
- let the existing public-entry layer map the public hostname back to the local nginx service;
- verify both the local HTTPS route and the public HTTPS route.

It does not cover how to develop, package, supervise, or operate the application itself.

## Architecture Pattern

For a service named `<service>`:

- local nginx host: `<service>.<local-zone>`
- public automatic host: `<service>.<public-zone>`
- local nginx file: `<nginx-sites-dir>/<service>-local.conf`
- shared certificate: `<wildcard-cert-fullchain>` and `<wildcard-cert-privkey>`
- upstream: normally `http://127.0.0.1:<port>` unless the service intentionally listens elsewhere

Only add or update the local nginx service config for normal service onboarding. Do not add per-service DNS records, create per-service certificates, or edit the public tunnel configuration unless the user explicitly asks to change the shared infrastructure.

## Expected Preconditions

A machine-local copy of this skill should fill in and verify:

- wildcard DNS for the local zone, for example `*.<local-zone> -> <lan-ip>`
- wildcard DNS for the public zone, for example `*.<public-zone> -> <public-entry-ip>`
- a reusable wildcard certificate that covers both zones
- the nginx include convention and service config directory
- the public-entry mechanism, such as FRP, reverse proxy, gateway, or tunnel
- the certificate renewal command and install location

## Add A Service

1. Confirm the service upstream is healthy.

```bash
ss -ltnp | grep '<port>'
curl --noproxy '*' -sS http://127.0.0.1:<port>/<health-or-version>
```

2. Add only the local nginx config.

```nginx
server {
    listen 80;
    server_name <service>.<local-zone>;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
    }
}

server {
    listen 443 ssl;
    server_name <service>.<local-zone>;

    ssl_certificate <wildcard-cert-fullchain>;
    ssl_certificate_key <wildcard-cert-privkey>;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
    }
}
```

3. Test and reload nginx gracefully.

```bash
sudo nginx -t
sudo systemctl reload nginx
systemctl is-active nginx
```

4. Verify the local route with proxy bypass.

```bash
curl --noproxy '*' -sS --resolve <service>.<local-zone>:443:127.0.0.1 \
  https://<service>.<local-zone>/<health-or-version>
```

5. Verify the public automatic route without DNS or tunnel changes.

```bash
curl -sS https://<service>.<public-zone>/<health-or-version>
```

Then open the public URL in a browser when user-facing access matters.

## Final Response

When the service is verified, give the user the final public URL as a bare clickable link, not inside inline code or a fenced code block. This applies to the final user-facing link; commands, paths, and config snippets can still use code formatting.

Example final link:

https://<service>.<public-zone>

## Do Not

- Do not add per-service DNS records when wildcard DNS already covers the host.
- Do not create per-service certificates when a shared wildcard certificate covers the host.
- Do not edit tunnel/public-entry configuration for normal service onboarding.
- Do not print or store certificate private keys, DNS provider tokens, tunnel tokens, API tokens, or passwords in logs or chat.
- Do not leave the common skill with machine-specific paths; put those in the local copy.
