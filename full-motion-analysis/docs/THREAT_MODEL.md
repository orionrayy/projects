# Threat Model and Privacy Boundaries

## Assets

Video files, audio tracks, file paths, generated reports, hashes, MCP tool output, dependency/tool versions, environment variables, and any future upload jobs.

## Threats and controls in v0.1

- **Arbitrary local file reads:** MCP tools resolve source paths and only permit files within MOTION_ALLOWED_ROOTS. Configure roots narrowly. No URL-fetch tool exists.
- **Path traversal / symlinks:** canonical path resolution occurs before checking path membership against canonical allowed roots.
- **Command injection:** FFmpeg and FFprobe are invoked using argument arrays, never shell-interpolated commands.
- **Resource exhaustion:** analysis frame cap, bounded grayscale dimensions, capped sampling rate, one-frame decode streaming, subprocess timeouts, and one FFmpeg thread are used. The frame cap should be lowered for constrained systems.
- **False certainty:** output uses event candidates and rule IDs, records sampling coverage, and includes explicit measurement limits.
- **Media privacy:** source files are not uploaded, copied into the repository, or sent to any external provider by the local pipeline. Reports default to a local report directory.
- **Public MCP misuse:** no public remote endpoint is part of v0.1. The Streamable HTTP option is for controlled local testing only.

## Residual risks

FFmpeg/FFprobe parse untrusted media. Keep them updated; analyze untrusted uploads in an isolated process/container with OS-level CPU, memory, disk, and wall-time limits. A Python frame cap does not prevent every decoder-level resource attack. The local MCP server has the OS privileges of its user, so allowed-root checks reduce but do not replace process isolation.

SHA-256 is provenance/integrity metadata; it is not a privacy guarantee and should not be treated as anonymization. Reports include a filename and may contain timestamps, so handle and delete them as user data.

## Before remote launch

Authentication, upload quotas, random job identifiers, temporary object storage with lifecycle deletion, per-user access control, network egress policy, malware/decoder isolation, abuse handling, deployment secrets, audit logging that excludes media content, retention notices, and a tested delete path are release blockers.
