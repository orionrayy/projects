# MCP Integration

## Current local integration

The MCP server uses the official Python SDK and stdio transport by default. It exposes:
- inspect_video_metadata(video_path)
- analyze_local_video(video_path, max_fps, optical_flow, max_frames)
- audit_ffmpeg_render(video_path, expected_width, expected_height, expected_fps, expected_duration_s, require_audio, max_fps)

Install and configure the server locally:

~~~bash
python -m pip install -e ".[vision,mcp]"
# POSIX example; use the path-list separator for the host OS.
export MOTION_ALLOWED_ROOTS="$HOME/Videos:$HOME/Downloads:/absolute/path/to/render-outputs"
export MOTION_REPORT_DIR="$HOME/.motion-evidence-lab/reports"
python mcp_server.py
~~~

The server is intended to be launched as an MCP stdio subprocess by an MCP host; it does not print analysis logs to stdout. The host's MCP configuration should invoke the Python entry point in the checked-out project directory, for example:

~~~json
{
  "mcpServers": {
    "motion-evidence-lab": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/projects/full-motion-analysis",
        "run",
        "python",
        "mcp_server.py"
      ],
      "env": {
        "MOTION_ALLOWED_ROOTS": "/ABSOLUTE/PATH/videos:/ABSOLUTE/PATH/render-outputs",
        "MOTION_REPORT_DIR": "/ABSOLUTE/PATH/motion-reports"
      }
    }
  }
}
~~~

Replace all example paths with real paths and install the project dependencies in that environment. Set MOTION_ALLOWED_ROOTS to the smallest directories needed. Symlinks are resolved before the boundary check. The report directory is separate from source media.

## Remote MCP and ChatGPT connector status

This bootstrap is **not yet a remotely hosted MCP server and is not automatically connected to ChatGPT**. A local stdio server can analyze a path visible to the machine running that server. It cannot automatically read a video uploaded into a separate ChatGPT conversation or access a path on another machine.

To make the tool callable from a remote ChatGPT MCP connector, the project needs a secure deployed Streamable HTTP endpoint plus a deliberate video handoff mechanism (authenticated upload or short-lived object reference). Before public deployment, implement:
1. authentication and per-user authorization;
2. upload size/time limits and temporary storage;
3. asynchronous job IDs, cancellation, concurrency limits and quota controls;
4. strict retention/cleanup and explicit consent for media storage;
5. isolated FFmpeg workers and patched decoders;
6. egress restrictions / SSRF defenses if remote URLs are ever accepted;
7. report ownership checks and non-guessable IDs;
8. no secret or uploaded-video logging.

Do not expose MOTION_MCP_TRANSPORT=streamable-http to the public internet on an untrusted network. Local path restrictions are not a substitute for remote authentication. The SDK supports Streamable HTTP, but that protocol support alone does not provide video upload, authorization, storage, or compute isolation.

## Using it to audit FFmpeg projects

Run analysis against the final muxed artifact, not only the silent visual master:

~~~bash
motionlab audit output/final.mp4 --expected-width 1920 --expected-height 1080 --expected-fps 24 --expected-duration 390 --require-audio --output reports/final-audit.json
~~~

Adjust duration and technical expectations to the actual delivery contract. An absent audio stream is a release-blocking error only when --require-audio is set. A technical pass still requires human review for composition, readability, story continuity, audio intelligibility, and character anatomy.
