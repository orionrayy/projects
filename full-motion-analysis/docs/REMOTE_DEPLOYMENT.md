# Remote MCP Deployment and Video Handoff

## Tools and request flow

Remote Streamable HTTP MCP endpoint: \`/mcp\`. A bearer token is mandatory. The service also exposes a minimal health endpoint and a short-lived one-use browser-upload capability. It never fetches arbitrary URLs or accepts arbitrary filesystem paths.

MCP tools:
- \`create_video_upload_ticket()\`: creates a browser upload page valid for 15 minutes.
- \`inspect_uploaded_video(upload_id)\`: returns metadata, SHA-256, and remaining retention.
- \`analyze_uploaded_video(upload_id, max_fps=30, optical_flow=true)\`: returns timestamped motion evidence and a report ID.
- \`audit_uploaded_ffmpeg_render(upload_id, expected_width=1920, expected_height=1080, expected_fps=24, expected_duration_s=null, require_audio=true)\`: validates the delivery contract.
- \`get_motion_report_section(report_id, section, offset, limit)\`: retrieves a summary or a bounded events/timeline page.

## Upload workflow

1. Call \`create_video_upload_ticket\` from an authenticated MCP client.
2. Open the returned \`upload_page_url\` in a browser where the file is accessible.
3. Select a video. Guardrails: 25 MiB maximum, up to 120 seconds, at most 3840×2160, maximum 120 FPS, supported container extension, and FFprobe validation.
4. Copy the returned \`upload_id\` into the conversation and invoke analysis or audit.
5. Use \`report_id\` to retrieve pages of evidence.
6. Files and reports are temporary and expire after one hour, but may disappear earlier after a service restart/redeploy/sleep on an ephemeral free instance.

The ticket URL is a secret capability until consumed or expired. Anyone with it can use it during that window; do not share it. It is single-use and attempt-limited. It is separate from the MCP bearer token.

## Render Blueprint

\`render.yaml\` describes a free-plan Docker web service, Singapore region, generated \`MOTION_API_TOKEN\`, bounded upload/retention settings and \`/health\` health check. It is prepared but **not deployed**.

Before deploy, confirm the intended Render workspace. After deployment, retrieve the generated token through Render's service environment settings and configure the remote MCP client to use it as the bearer credential. Never commit the token, place it in source, or share it in a conversation. No unauthenticated public \`/mcp\` access is permitted.

The remote service has streamed upload size limits, FFprobe duration/resolution/FPS validation, a single concurrent analysis gate, temporary storage, report TTL cleanup, a non-root container user and MCP Host/DNS-rebinding protection. These controls do not eliminate all parser vulnerabilities; keep FFmpeg updated and isolate untrusted media.

## ChatGPT connector availability

A deployed MCP server is not automatically registered with ChatGPT. Current official documentation lists full custom MCP connections on ChatGPT Business and Enterprise/Edu web workspaces; Pro has more limited read/fetch support, while Go is not listed. Check the current plan/workspace controls. This endpoint can still be used by another MCP client that supports Streamable HTTP and bearer authentication.

The upload page is a deliberate handoff because an MCP call does not automatically transfer the binary contents of an arbitrary video attachment to a separate server. The user must select the file in the one-use browser page and then provide the returned upload ID.

## Local alternative

For a file already on the computer running the MCP host, use \`python mcp_server.py\` and configure \`MOTION_ALLOWED_ROOTS\`. The local stdio server has no public endpoint and can only access media visible on that host.

## Smoke test

~~~bash
curl -fsS https://YOUR_RENDER_HOST/health
curl -i https://YOUR_RENDER_HOST/mcp
~~~

Health should return \`{"status":"ok","service":"motion-evidence-lab"}\`; an MCP request without a valid bearer credential should be rejected. Then test discovery, ticket creation, upload, analysis, paginated report access and cleanup with a non-sensitive short clip.
