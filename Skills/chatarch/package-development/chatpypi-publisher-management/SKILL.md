---
name: chatpypi-publisher-management
description: "Manage PyPI Trusted Publishers with ChatPyPI sessions: list projects/publishers, inspect details, add/update GitHub publisher entries, and verify safely."
version: 0.1.0
---

# ChatPyPI Publisher Management

## When To Use

Use this skill when the user asks to view, add, update, or verify PyPI publishing / Trusted Publisher configuration for ChatArch packages, especially phrases like:

- "project list / publisher list"
- "publish list"
- "trusted publisher"
- "把某个项目加到 PyPI publish"
- "给 ChatArch/<Repo> 配 PyPI 发布"
- "查看 pending publisher / active publisher"

This skill covers PyPI-side publisher configuration. Pair it with `python-package-publishing` for release gates and `github-workflows` when repository workflows or PRs/tags are involved. For broader ChatArch package-development routing, consult the ChatMemory theme index `Skills/chatarch/package-development/README.md` when available.

## Core Rule

Do not guess the GitHub owner/repository from the PyPI username or session profile.

For ChatArch packages, the PyPI Trusted Publisher owner is normally `ChatArch`, not `RexWzh` and not the PyPI project name as an owner. Example:

```text
PyPI project: ChatSage / chatsage
GitHub owner: ChatArch
GitHub repository: ChatSage
Workflow filename: publish.yml
Environment: blank / (Any), unless the existing project/workflow explicitly uses an environment
```

`RexWzh/askchat` is an existing exception, not the pattern to copy to ChatArch packages.

## Safety Rules

- Never print `PYPI_SESSION_TOKEN`, cookies, CSRF token values, passwords, TOTP secrets, or API tokens.
- Use a named ChatEnv profile such as `-e RexWzh` for account-specific PyPI management.
- Before writing to PyPI, confirm the logged-in account with `auth whoami -e <profile>`.
- Treat adding/removing/updating Trusted Publishers as a real remote mutation.
- Prefer blank environment for the current ChatArch baseline when existing similar projects show `(Any)`. Use `environment: pypi` only when the GitHub workflow and PyPI publisher are both explicitly configured for that environment.
- Do not assume PyPI exposes a public JSON API for publisher configuration. Current practical path is authenticated PyPI web forms plus post-write readback.

## Read Current State

Use the installed ChatPyPI from the ChatArch operator venv unless the task explicitly targets a local source checkout:

```bash
BIN=/Users/rexwzh/.chatarch/venv/bin/chatpypi

$BIN auth whoami -e RexWzh --format json
$BIN project list -e RexWzh --format json
$BIN publisher list -e RexWzh --format json
$BIN publisher pending-list -e RexWzh --format json
```

Important distinction:

- `publisher list` overview returns active/pending counts and active project names.
- Repository/workflow/environment details are on each project settings page and may require per-project fetches:

```text
https://pypi.org/manage/project/<project>/settings/publishing/
```

## Inspect Publisher Details

For a given PyPI project, fetch the settings page with the ChatPyPI session payload and extract safe text only:

```python
from html.parser import HTMLParser
from chatpypi.session_ops import load_session_payload_from_env, requests_session_from_payload

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip = True
    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            value = " ".join(data.split())
            if value:
                self.text.append(value)

payload = load_session_payload_from_env(env_profile="RexWzh")
session = requests_session_from_payload(payload)
resp = session.get("https://pypi.org/manage/project/ChatSage/settings/publishing/", timeout=30)
resp.raise_for_status()
parser = TextParser()
parser.feed(resp.text)
for i, value in enumerate(parser.text):
    if value in {"Publisher Details", "GitHub", "Repository:", "Workflow:", "Environment name:"} or "ChatArch/ChatSage" in value or "publish.yml" in value:
        print(i, value)
```

Expected successful detail shape for ChatArch projects:

```text
GitHub
Repository:
ChatArch/<Repo>
Workflow:
publish.yml
Environment name:
[Any or blank on page, reported as (Any) in summaries]
```

## Add a GitHub Trusted Publisher

1. Confirm target from the user or from the ChatArch repo convention:

```text
PyPI project: chatsage / ChatSage
GitHub owner: ChatArch
GitHub repo: ChatSage
Workflow filename: publish.yml
Environment: blank unless explicitly required
```

2. Fetch the project publishing settings page:

```python
from html.parser import HTMLParser
from urllib.parse import urljoin
from chatpypi.session_ops import load_session_payload_from_env, requests_session_from_payload

class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.cur = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.cur = {"method": attrs.get("method", "get").lower(), "action": attrs.get("action", ""), "inputs": []}
        elif self.cur is not None and tag == "input":
            self.cur["inputs"].append({"name": attrs.get("name", ""), "type": attrs.get("type", ""), "value": attrs.get("value", "")})
    def handle_endtag(self, tag):
        if tag == "form" and self.cur is not None:
            self.forms.append(self.cur)
            self.cur = None

payload = load_session_payload_from_env(env_profile="RexWzh")
session = requests_session_from_payload(payload)
url = "https://pypi.org/manage/project/chatsage/settings/publishing/"
resp = session.get(url, timeout=30)
resp.raise_for_status()
parser = FormParser()
parser.feed(resp.text)
form = None
for candidate in parser.forms:
    names = {item["name"] for item in candidate["inputs"]}
    if {"csrf_token", "owner", "repository", "workflow_filename", "environment"} <= names:
        form = candidate
        break
if form is None:
    raise SystemExit("GitHub trusted publisher form not found")
csrf = next(item["value"] for item in form["inputs"] if item["name"] == "csrf_token")
action = urljoin(resp.url, form["action"])
post = session.post(
    action,
    data={
        "csrf_token": csrf,
        "owner": "ChatArch",
        "repository": "ChatSage",
        "workflow_filename": "publish.yml",
        "environment": "",
    },
    headers={"Referer": resp.url, "Origin": "https://pypi.org"},
    timeout=30,
    allow_redirects=True,
)
print("post_status", post.status_code)
print("final_url", post.url)
```

A final URL ending in `#errors` is not sufficient to determine failure because PyPI form actions often include that anchor. Always verify by readback.

## Verify After Write

Run both overview and detail verification.

Overview:

```bash
BIN=/Users/rexwzh/.chatarch/venv/bin/chatpypi
$BIN publisher list -e RexWzh --format json
$BIN publisher pending-list -e RexWzh --format json
```

Look for:

```text
active_count increased as expected
pending_count 0 unless deliberately adding a pending publisher
FOUND_ACTIVE_PROJECT ChatSage
```

Detail page must show:

```text
GitHub
Repository:
ChatArch/ChatSage
Workflow:
publish.yml
Environment name:
```

If the environment line is blank, summarize it as `(Any)`.

## ChatSage Example From 2026-06-26

Confirmed operation:

```text
Profile: RexWzh
PyPI project: ChatSage / chatsage
Added publisher:
  GitHub repository: ChatArch/ChatSage
  Workflow: publish.yml
  Environment: (Any)
Readback:
  active_count: 18
  pending_count: 0
  active project found: ChatSage
```

## Common Pitfalls

- Copying `RexWzh/askchat` as a pattern for ChatArch packages. It is an exception.
- Treating the PyPI username/profile as the GitHub owner.
- Assuming the overview page includes repository/workflow/environment details; it usually only includes project names and manage links.
- Treating `#errors` in the form action/final URL as failure without inspecting readback.
- Adding `environment: pypi` on the PyPI side while the GitHub workflow has no matching `environment: pypi`, or vice versa.
- Printing raw session/cookie/CSRF values during debugging.

## When To Improve ChatPyPI CLI

Current ChatPyPI 0.2.2 supports read paths but not a first-class publisher update command. A future CLI improvement could add:

```bash
chatpypi publisher detail <project> -e RexWzh --format json
chatpypi publisher add-github <project> --owner ChatArch --repo ChatSage --workflow publish.yml --environment "" -e RexWzh
```

Tests should cover overview-only vs detail-page behavior, ChatArch owner defaults, environment blank = `(Any)`, and no secret output.
