"""Authenticated remote MCP with one-use, short-lived browser upload capabilities."""
from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import threading
import time
import uuid
from urllib.parse import urlparse
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:
    from mcp.server.fastmcp import FastMCP as MCPServerClass
except ImportError:
    # MCP SDK v2 renamed FastMCP to MCPServer; retain v1 compatibility.
    from mcp.server.mcpserver import MCPServer as MCPServerClass
from mcp.server.transport_security import TransportSecuritySettings
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

from motionlab.analysis import analyze_video
from motionlab.audit import audit_video
from motionlab.media import probe_media, sha256_file


def _env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except (ValueError, TypeError):
        value = default
    return max(minimum, min(maximum, value))


SERVICE_NAME = "motion-evidence-lab"
MAX_UPLOAD_BYTES = _env_int("MOTION_MAX_UPLOAD_BYTES", 25 * 1024 * 1024, minimum=1024, maximum=100 * 1024 * 1024)
UPLOAD_TTL_SECONDS = _env_int("MOTION_UPLOAD_TTL_SECONDS", 3600, minimum=60, maximum=86400)
TICKET_TTL_SECONDS = _env_int("MOTION_TICKET_TTL_SECONDS", 900, minimum=60, maximum=3600)
MAX_VIDEO_DURATION_SECONDS = _env_int("MOTION_MAX_VIDEO_DURATION_SECONDS", 120, minimum=1, maximum=600)
MAX_ACTIVE_UPLOADS = _env_int("MOTION_MAX_ACTIVE_UPLOADS", 4, minimum=1, maximum=12)
UPLOAD_ROOT = Path(os.environ.get("MOTION_UPLOAD_ROOT", "/tmp/motion-evidence-lab/uploads")).expanduser().resolve()
REPORT_ROOT = Path(os.environ.get("MOTION_REPORT_DIR", "/tmp/motion-evidence-lab/reports")).expanduser().resolve()
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mpeg", ".mpg"}
ID_PATTERN = re.compile(r"^[a-f0-9]{32}$")
TICKET_PATTERN = re.compile(r"^[A-Za-z0-9_-]{40,64}$")
_STATE_LOCK = threading.RLock()
_JOB_LOCK = threading.Lock()
_TICKETS: dict[str, dict[str, Any]] = {}
_UPLOADS: dict[str, dict[str, Any]] = {}
_REPORTS: dict[str, dict[str, Any]] = {}
_ACTIVE_UPLOADS: set[str] = set()

mcp = MCPServerClass(
    SERVICE_NAME,
    instructions=(
        "Open-world relational video analysis over bounded RGB space-time volumes. The v0.2 core uses "
        "multiscale spatial-temporal signatures and regional relations rather than pairwise optical flow as "
        "its primary representation. Call create_video_upload_ticket, open its upload_page_url and select a "
        "video, then pass the returned upload_id to analysis. Learned prototypes, when present, are corpus-relative "
        "and non-semantic; do not infer physical speed, object identity, universal domain accuracy or causality."
    ),
)


def _api_token() -> str | None:
    token = os.environ.get("MOTION_API_TOKEN", "")
    return token if len(token) >= 32 else None


def _public_base_url() -> str:
    value = os.environ.get("MOTION_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if value.startswith(("https://", "http://")):
        return value
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
    if host and not any(char in host for char in "/?#@"):
        return f"https://{host}"
    return "http://127.0.0.1:8000"


def _allowed_hosts() -> list[str]:
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
    explicit = os.environ.get("MOTION_ALLOWED_HOSTS", "")
    values = [item.strip() for item in explicit.split(",") if item.strip()]
    if host and not any(char in host for char in "/?#@"):
        values.extend([host, f"{host}:*"])
    if not values:
        values = ["localhost:*", "127.0.0.1:*", "[::1]:*"]
    return sorted(set(values))


def _allowed_origins() -> list[str]:
    explicit = os.environ.get("MOTION_ALLOWED_ORIGINS", "")
    origins = [item.strip() for item in explicit.split(",") if item.strip()]
    public_base = os.environ.get("MOTION_PUBLIC_BASE_URL", "").strip()
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
    if public_base:
        parsed = urlparse(public_base)
        if parsed.scheme in {"https", "http"} and parsed.netloc:
            origins.append(f"{parsed.scheme}://{parsed.netloc}")
    if hostname and not any(char in hostname for char in "/?#@"):
        origins.append(f"https://{hostname}")
    if not origins:
        origins = ["http://localhost:*", "http://127.0.0.1:*", "http://[::1]:*"]
    return sorted(set(origins))


def safe_extension(filename: str) -> str | None:
    """Extract only a whitelisted suffix; user input is never used as a filesystem path."""
    basename = filename.replace("\\", "/").rsplit("/", 1)[-1]
    suffix = Path(basename).suffix.lower()
    if suffix in ALLOWED_EXTENSIONS:
        return suffix
    guessed = mimetypes.guess_extension(basename.lower().split(";", 1)[0])
    return guessed if guessed in ALLOWED_EXTENSIONS else None


def _safe_id(value: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise ValueError("invalid_id_format")
    return value


def _remove_file(path: Path | None) -> None:
    if path is None:
        return
    try:
        resolved = path.resolve()
        if resolved.is_relative_to(UPLOAD_ROOT) or resolved.is_relative_to(REPORT_ROOT):
            resolved.unlink(missing_ok=True)
    except OSError:
        pass


def cleanup_expired(now: float | None = None) -> None:
    current = time.time() if now is None else now
    with _STATE_LOCK:
        for ticket, state in list(_TICKETS.items()):
            if float(state["expires_at"]) <= current:
                _TICKETS.pop(ticket, None)
        for upload_id, state in list(_UPLOADS.items()):
            if float(state["expires_at"]) <= current and upload_id not in _ACTIVE_UPLOADS:
                _UPLOADS.pop(upload_id, None)
                _remove_file(Path(state["path"]))
        for report_id, state in list(_REPORTS.items()):
            if float(state["expires_at"]) <= current:
                _REPORTS.pop(report_id, None)
                _remove_file(Path(state["path"]))


@contextmanager
def claim_upload(upload_id: str) -> Iterator[dict[str, Any]]:
    cleanup_expired()
    _safe_id(upload_id)
    if not _JOB_LOCK.acquire(blocking=False):
        raise RuntimeError("service_busy_try_again_shortly")
    try:
        with _STATE_LOCK:
            state = _UPLOADS.get(upload_id)
            if state is None:
                raise ValueError("upload_not_found_or_expired")
            _ACTIVE_UPLOADS.add(upload_id)
            snapshot = dict(state)
        try:
            yield snapshot
        finally:
            with _STATE_LOCK:
                _ACTIVE_UPLOADS.discard(upload_id)
    finally:
        _JOB_LOCK.release()


def _store_report(report: dict[str, Any], kind: str) -> dict[str, Any]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    report_id = uuid.uuid4().hex
    destination = (REPORT_ROOT / f"{report_id}.json").resolve()
    if not destination.is_relative_to(REPORT_ROOT):
        raise RuntimeError("report_path_policy_violation")
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(destination)
    expires_at = time.time() + UPLOAD_TTL_SECONDS
    with _STATE_LOCK:
        _REPORTS[report_id] = {
            "path": str(destination), "expires_at": expires_at, "kind": kind,
            "input_sha256": report.get("input", {}).get("sha256"),
        }
    return {"report_id": report_id, "expires_in_seconds": UPLOAD_TTL_SECONDS}


async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": SERVICE_NAME})


async def upload_page(request: Request) -> Response:
    ticket = request.path_params.get("ticket", "")
    if not TICKET_PATTERN.fullmatch(ticket):
        return JSONResponse({"status": "ERROR", "error": "upload_ticket_invalid_or_expired"}, status_code=404)
    cleanup_expired()
    with _STATE_LOCK:
        state = _TICKETS.get(ticket)
        if not state or state.get("used") or state.get("in_use"):
            return JSONResponse({"status": "ERROR", "error": "upload_ticket_invalid_or_expired"}, status_code=404)
        expires_in = max(0, int(float(state["expires_at"]) - time.time()))
    if request.method == "GET":
        size_mb = round(MAX_UPLOAD_BYTES / (1024 * 1024), 1)
        body = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer">
<title>Motion Evidence Lab — Video upload</title>
<style>body{{font:16px system-ui,sans-serif;max-width:640px;margin:7vh auto;padding:20px;line-height:1.5;color:#17202a}}
main{{border:1px solid #d8dee9;border-radius:14px;padding:24px}}button{{padding:10px 16px}}small{{color:#536273}}
#result{{white-space:pre-wrap;overflow-wrap:anywhere}}</style>
<main><h1>Motion Evidence Lab</h1><p>Single-use upload ticket. Expires in about {expires_in} seconds.</p>
<p><label for="file">Choose a video (maximum {size_mb} MiB, duration ≤ {MAX_VIDEO_DURATION_SECONDS}s).</label></p>
<input id="file" type="file" accept="video/*,.mkv,.avi,.m4v,.mpeg,.mpg"><p><button id="send">Upload video</button></p>
<small>Temporary storage, maximum retention {UPLOAD_TTL_SECONDS//60} minutes. The ticket is a secret capability; do not share it.</small>
<div id="result" role="status"></div></main>
<script>
const ticket={json.dumps(ticket)};
document.getElementById('send').addEventListener('click',async()=>{{
 const file=document.getElementById('file').files[0], out=document.getElementById('result'), button=document.getElementById('send');
 if(!file){{out.textContent='Select a video first.';return;}}
 if(file.size>{MAX_UPLOAD_BYTES}){{out.textContent='File exceeds upload limit.';return;}}
 button.disabled=true;out.textContent='Uploading and validating video…';
 try{{
  const response=await fetch('/upload/'+ticket+'?filename='+encodeURIComponent(file.name),
   {{method:'POST',headers:{{'Content-Type':file.type||'application/octet-stream'}},body:file,cache:'no-store'}});
  const result=await response.json();out.textContent=JSON.stringify(result,null,2);
  if(!response.ok)button.disabled=false;
 }}catch(error){{out.textContent='Upload failed: '+String(error);button.disabled=false;}}
}});
</script></html>"""
        return HTMLResponse(body, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff"})
    if request.method != "POST":
        return JSONResponse({"status": "ERROR", "error": "method_not_allowed"}, status_code=405)
    try:
        header = request.headers.get("content-length")
        if header and int(header) > MAX_UPLOAD_BYTES:
            return JSONResponse({"status": "ERROR", "error": "upload_too_large", "max_bytes": MAX_UPLOAD_BYTES}, status_code=413)
    except ValueError:
        return JSONResponse({"status": "ERROR", "error": "invalid_content_length"}, status_code=400)

    filename = request.query_params.get("filename", "")
    extension = safe_extension(filename)
    if extension is None:
        return JSONResponse({"status": "ERROR", "error": "unsupported_video_extension", "allowed": sorted(ALLOWED_EXTENSIONS)}, status_code=415)
    with _STATE_LOCK:
        state = _TICKETS.get(ticket)
        if not state or state.get("used") or state.get("in_use") or float(state["expires_at"]) <= time.time():
            return JSONResponse({"status": "ERROR", "error": "upload_ticket_invalid_or_expired"}, status_code=404)
        if len(_UPLOADS) >= MAX_ACTIVE_UPLOADS:
            return JSONResponse({"status": "ERROR", "error": "active_upload_limit_reached"}, status_code=429)
        state["in_use"] = True
        state["attempts"] = int(state.get("attempts", 0)) + 1
        if state["attempts"] > 3:
            state["used"] = True
            state["in_use"] = False
            return JSONResponse({"status": "ERROR", "error": "upload_ticket_attempt_limit"}, status_code=429)

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    upload_id = uuid.uuid4().hex
    target = (UPLOAD_ROOT / f"{upload_id}{extension}").resolve()
    if not target.is_relative_to(UPLOAD_ROOT):
        with _STATE_LOCK:
            _TICKETS.pop(ticket, None)
        return JSONResponse({"status": "ERROR", "error": "upload_path_policy_violation"}, status_code=400)

    total = 0
    try:
        with target.open("xb") as handle:
            async for chunk in request.stream():
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise OverflowError("upload_too_large")
                handle.write(chunk)
        if total == 0:
            raise ValueError("empty_upload")
        media = probe_media(target)
        duration = media.get("duration_s")
        fps = media.get("source_fps")
        if duration is None or float(duration) > MAX_VIDEO_DURATION_SECONDS:
            raise ValueError("video_duration_missing_or_exceeds_limit")
        if media["width"] > 3840 or media["height"] > 2160:
            raise ValueError("video_resolution_exceeds_4k_limit")
        if fps is not None and float(fps) > 120:
            raise ValueError("video_frame_rate_exceeds_120_fps_limit")
        digest = sha256_file(target)
        expires_at = time.time() + UPLOAD_TTL_SECONDS
        safe_name = Path(filename.replace("\\", "/")).name[:160]
        with _STATE_LOCK:
            _UPLOADS[upload_id] = {
                "path": str(target), "sha256": digest, "filename": safe_name,
                "media": media, "expires_at": expires_at, "size_bytes": total,
            }
            _TICKETS.pop(ticket, None)
        cleanup_expired()
        return JSONResponse({
            "status": "UPLOADED", "upload_id": upload_id, "filename": safe_name,
            "size_bytes": total, "sha256": digest, "media": media,
            "expires_in_seconds": UPLOAD_TTL_SECONDS,
            "next_step": "Pass upload_id to an MCP analysis/audit tool.",
        }, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
    except OverflowError:
        _remove_file(target)
        with _STATE_LOCK:
            if ticket in _TICKETS:
                _TICKETS[ticket]["in_use"] = False
        return JSONResponse({"status": "ERROR", "error": "upload_too_large", "max_bytes": MAX_UPLOAD_BYTES}, status_code=413)
    except (OSError, RuntimeError, ValueError) as exc:
        _remove_file(target)
        with _STATE_LOCK:
            if ticket in _TICKETS:
                _TICKETS[ticket]["in_use"] = False
        reason = str(exc)[:240] if isinstance(exc, ValueError) else "video_validation_failed"
        return JSONResponse({"status": "ERROR", "error": reason}, status_code=400)


class BearerTokenMiddleware:
    """Require a high-entropy bearer token on MCP and other non-public routes."""
    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        method = scope.get("method", "GET").upper()
        public_upload = path.startswith("/upload/") and method in {"GET", "POST"}
        if path == "/health" and method == "GET" or public_upload:
            await self.app(scope, receive, send)
            return
        expected = _api_token()
        if expected is None:
            response = JSONResponse({"status": "ERROR", "error": "server_authentication_not_configured"}, status_code=503)
            await response(scope, receive, send)
            return
        authorization = Headers(scope=scope).get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token or not hmac.compare_digest(token, expected):
            response = JSONResponse({"status": "ERROR", "error": "unauthorized"}, status_code=401,
                                    headers={"WWW-Authenticate": "Bearer", "Cache-Control": "no-store"})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


@mcp.tool()
def create_video_upload_ticket() -> dict[str, Any]:
    """Create a 15-minute single-use upload URL. Open it, select a video, then pass the returned upload_id to an analysis tool."""
    cleanup_expired()
    with _STATE_LOCK:
        if len(_TICKETS) >= 32:
            raise RuntimeError("too_many_active_upload_tickets")
        ticket = secrets.token_urlsafe(36)
        _TICKETS[ticket] = {
            "expires_at": time.time() + TICKET_TTL_SECONDS,
            "used": False, "in_use": False, "attempts": 0,
        }
    return {
        "status": "READY_FOR_UPLOAD",
        "upload_page_url": f"{_public_base_url()}/upload/{ticket}",
        "expires_in_seconds": TICKET_TTL_SECONDS,
        "max_upload_bytes": MAX_UPLOAD_BYTES,
        "max_video_duration_seconds": MAX_VIDEO_DURATION_SECONDS,
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
    }


@mcp.tool()
def inspect_uploaded_video(upload_id: str) -> dict[str, Any]:
    """Inspect metadata, content hash and remaining retention for a previously uploaded video."""
    cleanup_expired()
    _safe_id(upload_id)
    with _STATE_LOCK:
        record = _UPLOADS.get(upload_id)
        if not record:
            raise ValueError("upload_not_found_or_expired")
        return {
            "upload_id": upload_id, "filename": record["filename"], "sha256": record["sha256"],
            "size_bytes": record["size_bytes"], "media": record["media"],
            "expires_in_seconds": max(0, int(record["expires_at"] - time.time())),
        }


@mcp.tool()
def analyze_uploaded_video(upload_id: str, max_fps: float = 30.0, optical_flow: bool = True) -> dict[str, Any]:
    """Measure timestamped motion, optional dense optical flow, affine-compensated local motion regions, and event candidates."""
    rate = float(max_fps)
    if not 1.0 <= rate <= 30.0:
        raise ValueError("max_fps_must_be_between_1_and_30")
    with claim_upload(upload_id) as record:
        report = analyze_video(record["path"], max_fps=rate, width=320, height=180, max_frames=3600, optical_flow=bool(optical_flow))
        stored = _store_report(report, "analysis")
    return {
        "status": "COMPLETED", **stored, "input": report["input"], "media": report["media"],
        "sampling": report["sampling"], "measurements": report["measurements"],
        "event_counts": report["event_counts"], "events": report["events"][:120],
        "events_truncated_in_response": len(report["events"]) > 120,
        "timeline_points": len(report["timeline"]), "provenance": report["provenance"],
        "interpretation_limits": report["interpretation_limits"],
        "next_step": "Use get_motion_report_section(report_id, section='timeline' or 'events', offset, limit) for paginated evidence.",
    }


@mcp.tool()
def audit_uploaded_ffmpeg_render(
    upload_id: str,
    expected_width: int = 1920,
    expected_height: int = 1080,
    expected_fps: float = 24.0,
    expected_duration_s: float | None = None,
    require_audio: bool = True,
) -> dict[str, Any]:
    """Audit an uploaded FFmpeg output against technical delivery settings, motion anomalies and the required audio stream."""
    if not (64 <= int(expected_width) <= 7680 and 64 <= int(expected_height) <= 4320):
        raise ValueError("expected_resolution_out_of_supported_range")
    if not (1.0 <= float(expected_fps) <= 120.0):
        raise ValueError("expected_fps_must_be_between_1_and_120")
    if expected_duration_s is not None and not (0.1 <= float(expected_duration_s) <= MAX_VIDEO_DURATION_SECONDS):
        raise ValueError("expected_duration_out_of_supported_range")
    with claim_upload(upload_id) as record:
        report = audit_video(
            record["path"], expected_width=int(expected_width), expected_height=int(expected_height),
            expected_fps=float(expected_fps), expected_duration_s=expected_duration_s,
            require_audio=bool(require_audio), max_fps=30.0, max_frames=3600,
        )
        stored = _store_report(report, "audit")
    return {
        "status": report["status"], **stored, "release_gate_passed": report["release_gate_passed"],
        "input": report["input"], "media": report["media"], "qc": report["qc"],
        "event_counts": report["analysis"]["event_counts"], "events": report["analysis"]["events"][:120],
        "events_truncated_in_response": len(report["analysis"]["events"]) > 120, "limits": report["limits"],
    }


@mcp.tool()
def get_motion_report_section(report_id: str, section: str = "summary", offset: int = 0, limit: int = 100) -> dict[str, Any]:
    """Read a stored report summary or a bounded page of events/timeline; reports expire automatically."""
    cleanup_expired()
    _safe_id(report_id)
    if section not in {"summary", "events", "timeline"}:
        raise ValueError("section_must_be_summary_events_or_timeline")
    if int(offset) < 0:
        raise ValueError("offset_must_be_nonnegative")
    page_limit = max(1, min(int(limit), 250))
    with _STATE_LOCK:
        record = _REPORTS.get(report_id)
    if not record:
        raise ValueError("report_not_found_or_expired")
    path = Path(record["path"]).resolve()
    if not path.is_relative_to(REPORT_ROOT):
        raise PermissionError("report_path_policy_violation")
    report = json.loads(path.read_text(encoding="utf-8"))
    is_audit = report.get("schema_version") == "fma.audit.v0.1"
    analysis = report.get("analysis", {}) if is_audit else report
    if section == "summary":
        result = {
            "report_id": report_id, "kind": record["kind"], "schema_version": report["schema_version"],
            "input": report.get("input", analysis.get("input")), "media": report.get("media", analysis.get("media")),
            "sampling": analysis.get("sampling"), "measurements": analysis.get("measurements"),
            "event_counts": analysis.get("event_counts"), "timeline_total": len(analysis.get("timeline", [])),
            "provenance": analysis.get("provenance"),
            "interpretation_limits": analysis.get("interpretation_limits", report.get("limits")),
            "expires_in_seconds": max(0, int(record["expires_at"] - time.time())),
        }
        if is_audit:
            result.update({"status": report["status"], "qc": report["qc"], "release_gate_passed": report["release_gate_passed"]})
        return result
    items = analysis.get(section, [])
    start = int(offset)
    return {
        "report_id": report_id, "section": section, "offset": start, "limit": page_limit,
        "total": len(items), "items": items[start:start + page_limit],
        "has_more": start + page_limit < len(items),
    }


# The MCP application is the top-level ASGI app so its own lifespan starts the session manager.
# Render's injected hostname is allowlisted; local stdio MCP remains available separately.
_http_app = mcp.streamable_http_app(
    json_response=True,
    stateless_http=True,
    max_request_body_size=1024 * 1024,
    transport_security=TransportSecuritySettings(allowed_hosts=_allowed_hosts(), allowed_origins=_allowed_origins()),
)
_http_app.router.routes.insert(0, Route("/health", health, methods=["GET"]))
_http_app.router.routes.insert(1, Route("/upload/{ticket}", upload_page, methods=["GET", "POST"]))
app = BearerTokenMiddleware(_http_app)
