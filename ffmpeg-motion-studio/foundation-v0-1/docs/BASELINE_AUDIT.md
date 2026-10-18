# Baseline Audit — Foundation Stage 0/1

Date: 2026-10-18. Repository: orionrayy/projects. Audited base commit: 64c953c2d81979dba0bc0e966f83644ee6f48db9.

The tracked ffmpeg-motion-studio subtree initially contained only scripts/render_cashier_explainer_v3.py. That source imports render_procedural_master_v2 as v2, which was absent from the audited subtree. The old renderer is therefore not reproducible from that subtree alone; this does not prove the dependency is absent everywhere. The old renderer was preserved and the new foundation is additive.

Prior audit recorded an animated transaction-value defect and a silent preview. Those are regression motivations, not newly reproduced in this stage. No model training, provider call, voiceover integration, artistic approval, photorealism, or full-film migration is claimed.