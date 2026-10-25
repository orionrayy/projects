"""Conservative local-file boundary for MCP tools."""
from __future__ import annotations

import os
from pathlib import Path


def allowed_roots_from_env() -> list[Path]:
    configured = os.environ.get("MOTION_ALLOWED_ROOTS", "").strip()
    if configured:
        roots = [Path(part).expanduser().resolve() for part in configured.split(os.pathsep) if part.strip()]
    else:
        home = Path.home()
        candidates = [Path.cwd(), home / "Videos", home / "Downloads"]
        roots = [p.resolve() for p in candidates if p.exists()]
    if not roots:
        raise RuntimeError("no_allowed_roots_configured_set_MOTION_ALLOWED_ROOTS")
    return roots


def resolve_allowed_video_path(path: str, roots: list[Path] | None = None) -> Path:
    if not isinstance(path, str) or not path.strip():
        raise ValueError("video_path_must_be_nonempty")
    supplied = Path(path).expanduser()
    target = supplied.resolve(strict=True)
    if not target.is_file():
        raise ValueError("video_path_must_be_a_file")
    trusted_roots = [r.resolve() for r in roots] if roots is not None else allowed_roots_from_env()
    for root in trusted_roots:
        try:
            target.relative_to(root)
            return target
        except ValueError:
            continue
    raise PermissionError("video_path_outside_MOTION_ALLOWED_ROOTS")
