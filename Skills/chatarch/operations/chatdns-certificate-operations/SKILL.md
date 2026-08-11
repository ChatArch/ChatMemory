---
name: chatdns-certificate-operations
description: Use when managing ChatDNS DNS records/certificates and installing existing certs onto service servers.
version: 0.1.0
---

# ChatDNS Certificate Operations

Use this skill when a ChatArch service needs DNS records or HTTPS certificates managed through ChatDNS, especially when the user distinguishes the local control plane from an SSH/server target.

## Boundaries

- Treat the ChatDNS control plane as the canonical certificate inventory and issuance surface; do not generate ad-hoc server-side certificates when a managed certificate already covers the host.
- Do not call an SSH/server target "local". Local means the current control-plane machine unless the user explicitly switches execution context.
- Do not print private keys, DNS API keys, ACME account keys, tokens, passwords, service admin secrets, or raw connection strings.
- Use placeholders in shared docs and reports: `<registered-domain>`, `<cert-name>`, `<service-host>`, `<server>`, `<server-cert-dir>`, `<port>`.
- Record concrete domains, hosts, cert paths, and copy destinations only in the task project report or a machine-local skill, not in shared ChatMemory skills.

## Inspect Existing Certificates

List candidate managed certificate files without printing private-key content:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path.home() / ".chatarch" / "certs"
for p in sorted(root.rglob("fullchain.pem")):
    print(p)
PY
```

Expected normalized layout:

```text
~/.chatarch/certs/<registered-domain>/<cert-name>/fullchain.pem
~/.chatarch/certs/<registered-domain>/<cert-name>/privkey.pem
~/.chatarch/certs/<registered-domain>/<cert-name>/cert.pem
~/.chatarch/certs/<registered-domain>/<cert-name>/chain.pem
```

Check certificate subject, expiry, and SAN only:

```bash
openssl x509 -in ~/.chatarch/certs/<registered-domain>/<cert-name>/fullchain.pem -noout -subject -dates -text \
  | grep -E 'subject=|notBefore=|notAfter=|DNS:'
```

On macOS, `openssl x509 -ext subjectAltName` may not be available; use `-text` and filter SAN lines instead.

## DNS Records

Use ChatDNS for DNS state rather than ad-hoc `ping`/`host` checks when the task is record management:

```bash
chatdns records <registered-domain>
chatdns records <service-host>
chatdns set <service-host> -t A -v <server-public-ip> -e <profile-or-env-file> -I
```

If a subdomain currently resolves through wildcard DNS, `chatdns records <service-host>` is the authoritative check for explicit records.

## Copy Certs To A Server

From the control plane, copy only the necessary `fullchain.pem` and `privkey.pem` to the target server. Stage under the user's service cert directory first when useful, then install to the server's Nginx cert store.

```bash
ssh <server> 'mkdir -p ~/.chatarch/certs/<registered-domain>/<cert-name> && chmod 700 ~/.chatarch/certs ~/.chatarch/certs/<registered-domain> ~/.chatarch/certs/<registered-domain>/<cert-name> 2>/dev/null || true'
scp ~/.chatarch/certs/<registered-domain>/<cert-name>/fullchain.pem <server>:~/.chatarch/certs/<registered-domain>/<cert-name>/fullchain.pem
scp ~/.chatarch/certs/<registered-domain>/<cert-name>/privkey.pem <server>:~/.chatarch/certs/<registered-domain>/<cert-name>/privkey.pem
ssh <server> 'sudo mkdir -p <server-cert-dir> && sudo cp ~/.chatarch/certs/<registered-domain>/<cert-name>/fullchain.pem <server-cert-dir>/fullchain.pem && sudo cp ~/.chatarch/certs/<registered-domain>/<cert-name>/privkey.pem <server-cert-dir>/privkey.pem && sudo chmod 644 <server-cert-dir>/fullchain.pem && sudo chmod 600 <server-cert-dir>/privkey.pem && sudo chown root:root <server-cert-dir>/fullchain.pem <server-cert-dir>/privkey.pem'
```

Verify on the server without printing key content:

```bash
stat -c '%a %U %G %n' <server-cert-dir>/fullchain.pem <server-cert-dir>/privkey.pem
openssl x509 -in <server-cert-dir>/fullchain.pem -noout -subject -dates -text | grep -E 'subject=|notBefore=|notAfter=|DNS:'
```

## Nginx HTTPS Pattern

Use the installed cert in a 443 vhost and redirect HTTP to HTTPS:

```nginx
server {
    listen 80;
    server_name <service-host>;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name <service-host>;

    ssl_certificate <server-cert-dir>/fullchain.pem;
    ssl_certificate_key <server-cert-dir>/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Ssl on;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

After writing config:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## App Canonical Host

For applications that generate absolute links, align the application canonical host with the public HTTPS domain before final acceptance.

Verify:

```bash
curl -I http://<service-host>/
curl -I https://<service-host>/
```

## Renewal Notes

- Renew certificates through the ChatDNS control plane, then copy the renewed files to servers that consume them.
- Record consumer servers and destination paths in the task report using redacted or placeholder-safe form for shared artifacts.
- Do not store private cert/key material or provider credentials in ChatMemory skills.
