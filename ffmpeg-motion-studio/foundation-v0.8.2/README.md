# Motion Studio Foundation — Natural Motion v0.8.2

Status: engineering candidate; visual acceptance remains pending.

This stage addresses visible defects found in the v0.8.1 contact sheets: narrow projected feet, a sharply folded free-arm pose, and torso/head action too subtle to read at overview scale. It adjusts gait projection, free-arm trajectory, phase-coupled torso/head motion, basket response and rendered silhouette widths.

## Run

- Node.js 20+: npm test
- Generate deterministic SVG sequences and geometry reports: npm run render:preview -- .working
- Hosted CI produces carry/free MP4 previews, contact sheets and JSON evidence with FFmpeg/librsvg.

## Acceptance boundary

New tests check readable foot separation, visible torso/head response and measurable free-arm counter-swing. These are regression gates, not a claim of naturalness. Full-speed human review must still inspect the videos/contact sheets for weight transfer, foot sliding, crossings, contact, proportion and temporal coherence. Pixel-level naturalness scoring, browser/FFmpeg parity, full editor UI and integration into the 240-second film remain open.
