# MCP Integration

## Local integration

The local stdio MCP server calls the same public v0.2 relational analysis functions as the CLI:
- inspect_video_metadata(video_path)
- analyze_local_video(video_path, max_fps, optical_flow, max_frames, model_path)
- audit_ffmpeg_render(video_path, expected_width, expected_height, expected_fps, expected_duration_s, require_audio, max_fps)

The legacy-compatible optical_flow argument is accepted but is not used as the primary v0.2 analysis path. Results summarize overlapping RGB space-time windows, region nodes/edges, cross-window relations and limits. The MCP response includes up to 128 windows; the full JSON report remains in MOTION_REPORT_DIR.

Install and configure:

~~~bash
python -m pip install -e ".[mcp]"
export MOTION_ALLOWED_ROOTS="$HOME/Videos:$HOME/Downloads:/absolute/path/to/render-outputs:/absolute/path/to/models"
export MOTION_REPORT_DIR="$HOME/.motion-evidence-lab/reports"
python mcp_server.py
~~~

The model file, like the video file, must resolve inside MOTION_ALLOWED_ROOTS. Configure roots narrowly; do not expose local-path MCP to the public internet.

Example host config:

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
        "MOTION_ALLOWED_ROOTS": "/ABSOLUTE/PATH/videos:/ABSOLUTE/PATH/render-outputs:/ABSOLUTE/PATH/models",
        "MOTION_REPORT_DIR": "/ABSOLUTE/PATH/motion-reports"
      }
    }
  }
}
~~~

Replace sample paths with actual local paths. Standard output is reserved for MCP protocol traffic.

## Training then scoring with MCP

The trainer is run locally over videos you have permission to process:

~~~bash
motionlab train /PATH/TO/authorized-videos --output-dir /PATH/TO/models/fma
~~~

Only after reviewing the training report and promotion gates, provide a permitted model path to analyze_local_video. The model returns anonymous corpus-relative prototype and novelty information. It does not provide semantic labels or calibrated probabilities.

## FFmpeg render audit

Run analysis against the final muxed artifact, not just a silent visual master:

~~~bash
motionlab audit output/final.mp4 --expected-width 1920 --expected-height 1080 --expected-fps 24 --expected-duration 390 --require-audio --output reports/final-audit.json
~~~

Technical release checks and space-time signatures help locate suspicious intervals. They do not certify aesthetics, anatomy, narrative continuity, text readability, educational correctness, voice intelligibility, or lip synchronization.

## Remote MCP status

The remote Streamable HTTP source and Docker/Render setup are separate from the local stdio workflow. They are not considered deployed until an actual endpoint passes health, authentication, one-use upload, analysis, report retrieval and cleanup smoke tests. MCP SDK protocol support does not automatically transfer a ChatGPT attachment to an independent server or connect that server to a ChatGPT workspace.

The remote-service upload, auth, resource and retention limits described in REMOTE_DEPLOYMENT.md still apply. The endpoint must never accept arbitrary file-system paths or arbitrary URL fetches.
