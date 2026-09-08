---
name: file-share-web-ui-auth
description: "Use when web file-share UIs need upload/auth UX."
version: 0.1.0
---

# File-Share Web UI Auth

Use when modifying a Dufs/WebDAV/file-sharing UI where file reads, directory browsing and mutations have different authentication boundaries. Pair with service-entry and frontend-visual-acceptance guidance. Inspect the running service and real CLI before assuming a particular gateway command or auth mode exists.

## Decide the operation matrix first

Treat these separately: concrete-file GET/HEAD/Range, directory HTML and embedded DATA, listing JSON, search, WebDAV enumeration, directory archives, upload, edit/move/delete, and account/session management. Do not interpret “needs login” as permission to lock every existing file URL or grant every logged-in account every mutation.

## Application-owned directory login

For public concrete-file links with private directory browsing:

1. The application's `serve` layer owns the login page, login/logout APIs, session lifecycle and directory authorization. Nginx/reverse proxies only forward traffic. Do not substitute `auth_basic`, `auth_request` or proxy-side credential validation for the requested application login system.
2. Reuse the existing service credential provider; avoid parallel account, endpoint or token settings. Use HttpOnly cookies with suitable Secure/SameSite flags, bounded expiry/session counts and server-side revocation. Do not store browser passwords in sessionStorage in this mode.
3. Enforce directory HTML/DATA, JSON, search, noscript, PROPFIND/WebDAV and archive restrictions on the server. Hiding buttons or table rows is not access control.
4. Preserve known concrete-file reads and existing authenticated HTTP clients. Safe absent-file GET/HEAD requests may need empty404 responses so existing clients can check a destination before authenticated PUT; do not turn every absent file into401. Existing directories, metadata selectors and unsafe paths remain gated.
5. Preserve backend operation permissions. A403 denial must not log out a valid session. Revoke on credential revalidation failure or an appropriate401 from a request that actually used that session's credentials, not from an unrelated anonymous file/token failure.
6. Protect cookie-authenticated writes against CSRF, reject unsafe return URLs, keep protected responses out of caches and isolate untrusted active file previews from the login origin's authority.
7. Test the application directly without Nginx, then verify actual public HTTPS separately. A loopback HTTP preview has its own configured origin; it is not proof of production Secure-cookie behavior. Avoid browser redirect interception that sends a follow-up navigation to an old public backend.
8. Check logout, browser history and refresh. Previously authenticated directory content must not reappear as an accessible page after session revocation.

## Legacy direct HTTP-auth UI

Use this branch only when the product intentionally has no server-side session model:

- Preserve real HTTP/WebDAV authentication challenges for external clients; do not globally remove WWW-Authenticate merely to hide browser dialogs.
- Use a visible custom login form and explicit auth headers for protected requests, not deliberate unauthenticated mutations that trigger native browser prompts.
- Keep captured credentials no longer than sessionStorage and restore the UI via a real auth check after reload/Home navigation. Never read/export browser storage databases.
- If credentialed XHR.open still triggers prompts, open XHR normally and set the auth header in one helper. For Dufs deployments that offer Basic and Digest, the UI may use explicit Basic over the secure public route while CLI clients retain Digest.
- Do not invoke Dufs LOGOUT from the page when it creates a native prompt. In this legacy mode clear the UI/sessionStorage; in application-session mode call the real server logout API.

## UI contract

- Credential forms must explicitly use POST and a same-origin action even when JavaScript intercepts normal submission. Test the no-script behavior so missing scripts cannot put passwords in URL queries; provide a clear no-script notice.
- Use explicit login/logout labels. Before auth, show a clear login affordance; after auth, the account control opens a dropdown and logout is a separate menu action.
- Directory pages need a visible drop zone and file chooser. A hidden input or page-wide drop listener is insufficient.
- If uploads are queued before authentication, resume only after verified login; errors must be visible and safe.
- Route protected XHR/fetch paths through one helper. In application-session mode all relevant helpers use the session and CSRF contract, not stale stored passwords.
- Keep custom assets in the owning package and verify built wheels include them. Use the backend's supported asset override mechanism rather than patching its binary.
- Scope UI fixes. Compare the live and candidate assets before treating an inherited fixed-width file table as a new regression. An auth task should not silently become a redesign; report retained horizontal scrolling honestly.

## Verification

- Anonymous root/directory navigation reaches login without returning directory data.
- Anonymous JSON/search/WebDAV/archive/mutation requests are denied by the application itself.
- Existing-account login succeeds; invalid credentials, malformed auth, expiry and CSRF fail closed without secret-bearing error bodies.
- Cookies/passwords are not exposed in DOM/storage/logs; server session revocation is tested, not inferred from a button label.
- Concrete-file GET/HEAD/Range and original hashes survive the change. Native Basic/Digest clients and a real bounded upload still work.
- Browser controls perform real login-session navigation, upload and logout. If real credentials cannot be typed by automation policy, verify them through the real login API, then test the same authenticated browser session; state this boundary honestly.
- Inspect login and management screenshots on the actual target. Distinguish offline mocks, loopback candidates and production checks.
- Use owned browser profiles and graceful shutdown. Inspect ambiguous write results before retrying, retain receipts, and clean only proven task artifacts.
- Read back the final proxy diff: forwarding changes only, no proxy authentication when the application owns login.

## Pitfalls

Do not equate a healthy process with a functioning permission matrix. Do not infer authentication from the mere presence of an Authorization header. Do not hide a real file/listing regression by changing tests; distinguish required behavior from an inherited layout constraint using direct source and runtime evidence. Do not expose directory screenshots or credential-bearing receipts as public artifacts.
