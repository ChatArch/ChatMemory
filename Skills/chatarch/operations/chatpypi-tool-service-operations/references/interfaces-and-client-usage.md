# ChatPyPI REST/MCP interfaces and clients

## REST tree

Authenticate every non-public call with a ChatAuth Bearer access token. Query paths accept GET or POST; mutation paths are POST-only.

```text
/api
├── tools                         GET: catalog, methods, input schema
├── pkg/probe                     GET/POST: exact package-name preflight
├── pkg/upload                    POST: wheel/sdist artifacts
├── project/list                  GET/POST: bound account projects
├── publisher/list                GET/POST: active Publishers
├── publisher/detail              GET/POST: existing project detail
├── publisher/add-github          POST: add/verify active Publisher
├── publisher/pending-list        GET/POST: pending Publishers
├── publisher/pending-add         POST: explicit pending Publisher case
├── publisher/pending-remove      POST: remove exact pending Publisher
├── doctor/check                  GET/POST: bound account/session check
└── docs/{links,examples,open}     GET/POST: documentation tools
/mcp/                            MCP StreamableHTTP
```

The implemented catalog has 13 server tools in the baseline release. Treat live `/api/tools` as authoritative as new releases arrive. MCP names use underscores, for example `pkg_probe`, `publisher_add_github`, `project_list`. Local-only tools and planned placeholders are not exported.

## HTTP client

```python
import os
import httpx

headers = {"Authorization": f"Bearer {os.environ['CHATPYPI_ACCESS_TOKEN']}"}
with httpx.Client(base_url="https://tools.example.test", headers=headers,
                  timeout=20, follow_redirects=False, trust_env=False) as client:
    catalog = client.get("/api/tools").raise_for_status().json()
    result = client.get("/api/pkg/probe", params={"package_name": "ChatPyPI"}).raise_for_status().json()
    print(result["exit_code"], result["stdout"])
```

`tool`, `exit_code`, `stdout`, `stderr` preserve CLI semantics. HTTP401/403/413/422 distinguish authentication, authorization, request size and input rejection. An HTTP200 with nonzero `exit_code` is a completed tool failure, not success. Do not follow redirects or retry write calls after ambiguous outcomes.

## MCP client (SDK2.3)

Inspect the installed SDK signatures when changing major versions. SDK2.3 uses `MCPServer` and an `httpx2` async client for StreamableHTTP.

```python
import asyncio
import os
import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def run():
    headers = {"Authorization": f"Bearer {os.environ['CHATPYPI_ACCESS_TOKEN']}"}
    async with httpx2.AsyncClient(headers=headers, timeout=20, trust_env=False) as http:
        async with streamable_http_client("https://tools.example.test/mcp/", http_client=http) as streams:
            read, write, *extra = streams
            async with ClientSession(read, write, read_timeout_seconds=20) as session:
                await session.initialize()
                catalog = await session.list_tools()
                result = await session.call_tool("docs_links", {})
                print(len(catalog.tools), result.structured_content["exit_code"])

asyncio.run(run())
```

For host-program integration, import `chatpypi.service.create_app`, `create_mcp_server` and `chatpypi.tool_service.invoke_tool`. The current execution adapter runs registered CLI capabilities in-process with serialized output capture; it is not shell passthrough. Existing domain methods remain reusable separately. Treat importing the package as trusted host code, not a sandbox.

## Upload contract

```json
{
  "artifacts": [
    {"filename": "example-1.0-py3-none-any.whl", "content_base64": "<base64 bytes>", "size": 1, "sha256": "<computed SHA256>"}
  ],
  "repository": "pypi",
  "skip_existing": false
}
```

The JSON above is a schema sketch, not a valid publication fixture: compute the exact byte size and digest. Normal service-mode CLI creates the payload from already-built local dist files.

- Maximum4 artifacts;10MiB each;20MiB total;30MiB HTTP body.
- Allow only distribution filenames; reject paths, symlinks, duplicate names, incorrect size/base64/digests.
- The server reconstructs owned temporary dist files under ChatArch home and cleans them after the call; it does not unzip archives, read client source paths or build remotely.
- Resolve the upload token from the bound backend PyPI profile; reject caller-selected profiles, custom repository URLs, usernames and credential-env selectors.
- Preserve independent real-PyPI side-effect authorization. Uploading to a token-authenticated service is still publication, not a safe connectivity test.

## Review pitfalls

Require a concrete remote probe name and strip client-only paths. Align parent HTTP trusted hosts with mounted MCP DNS-rebinding rules. Run the mounted MCP session manager through parent ASGI lifespan. Omit absent optional None defaults before strict input validation. Offload blocking JWKS retrieval and tool execution through bounded thread APIs. Preserve schemas, output and exit semantics when adapting CLI tools; do not turn the protocol layer into a new orchestration product.
