# Drawing Cartoons 2 — clean-room static findings for Motion Studio

## Scope and evidence class
These figures come from static parsing of one submitted APK and the example project/resource archives supplied with it. The APK was not installed or executed. The data below is a compact aggregate research record: source project archives, original character images, audio, raw DEX, and full project XML are intentionally excluded. Static names/invocation sites suggest subsystems; they do not prove runtime control flow or internal algorithms.

## Corpus profile
- APK archive: 76,263,689 bytes, 3,673 entries, ZIP CRC verified. Reported application package com.zalivka.animation2, version 0.22.15, version code 285; manifest declares min SDK 24, target SDK 33, 19 permissions and 121 components.
- 20 parsed scene-project examples (.ats): 663 serialized frame records and 643 neighbor-record transition comparisons. XML adjacency is a data comparison only; playback order has not been established.
- 10 pack containers (.atp) and 3 standalone template samples.
- 448 nested .ati resource occurrences; 435 distinct content hashes. Of those, 446 archives parsed with both model.xml and assets.xml.
- 153 model XML resources and 148 asset-binding XML resources.
- DEX inventory: 15 files, 45,239 class definitions. A targeted static scan covered 4,272 app-core methods with bytecode and found 16,022 internal invoke sites. Treat this as a subsystem map, not a reachable runtime call graph.
- Parsed template point counts: median 6, p90 30, max 128; estimated parent depth median 3, p90 7, max 26 in this sample.

## Design implications adopted by this branch
1. Keep scene frame timing and render timebase explicit. The stickman source is five stored poses and a field interframes=8; neither proves output FPS or exact source interpolation semantics.
2. Make landmark identity, point IDs, ordered landmark lists and parent edges explicit and validate their consistency.
3. Treat hierarchy, attachment relations, asset binding, camera, background and time remapping as different future concepts rather than collapsing them into one untyped graph.
4. Build tests for 6, 27 (depth 26), 30, 64 and 128 landmarks. These are stress points based on the inspected sample distribution, not claimed limits of the original app.
5. Validate the in-memory pose state, serialized SVG contract and actual FFmpeg/FFprobe output as separate layers.

## Unknowns to keep open
- XML document order vs numeric frame ID vs actual playback order.
- Exact meaning and units of interframes.
- Whether coordinates are scene-global, unit-local or parent-relative.
- Whether parent edges and master/slave attachment relations are separate graphs.
- Semantics of edgeAsset weights, offsets, flip and state fields.
- Named animation range, period and loop timing.
- Camera/background spaces and possible parallax.
- Speed control point mapping to media time.

The accompanying format-semantics-experiment-plan.json keeps a controlled experiment for each question. Do not encode a source-compatible rule from a field name alone.

## Provenance note
The supplied APK contained a native library named lib_LiteApks_Com.so, and a local signature report indicated SHA1withRSA with a 1024-bit RSA key. The signature fingerprint differs from a third-party directory listing for a package with the same version/code. Cause remains unknown; this is an integrity/provenance concern, not a malware finding. Do not install or execute the sample as part of Motion Studio CI.

## Training and licensing boundary
This is clean-room reference analysis, not training data from a public corpus and not model training. The only integrated animation geometry in this branch is the user's five-pose stickman sample, represented as a normalized landmark fixture. No APK logic or proprietary media is redistributed. A future dataset-ingestion job should require source provenance, rights review, hashes, transformation logs and an independent validation report.
