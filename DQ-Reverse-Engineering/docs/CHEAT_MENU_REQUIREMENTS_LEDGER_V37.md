# Cheat Menu UX v37 — requirements compliance ledger

- One Cheat Menu concept, not a separate Gold tab.
- All 222 entries, 14 categories, unique stable IDs.
- Dedicated inner scroll list; body/document stays fixed.
- Search across ID, label, description, category and tags.
- Category and risk filtering, favorite filter, changed/staging views, blocked view.
- Expandable technical details with type, default, bounds, step, units, options, declared parameters, scope, conflict group and adapter status.
- Ordinary numeric values: button-only `−10`, `−1`, `+1`, `+10`; changes interpreted in actual displayed units, not “number of configured steps”.
- Normalized percentage values use percentage points: 0.05 (5%) +1 -> 0.06 (6%).
- Gold: separate custom numeric keypad made of buttons; no system keyboard required in the workbench and no ordinary writable number field.
- Preset, undo/reset, local event log, JSON export.
- Every card warns that unverified handlers are blocked; all 222 items remain disconnected from gameplay.
- No APK/XAPK built.

## Native feasibility result

ARM64 library exports a native List element family and script APIs for List item add, item text, finger/smooth scrolling, selection and scroll position. Hence native scrolling itself is available. The missing piece is a validated model/runtime path that populates 222 IDs, displays selected details and dispatches them to safe game handlers. The custom Gold keyboard flow and actual Gold balance write are separately unverified.
