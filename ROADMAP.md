# Roadmap

Python desktop media converter (audio/video/image) with FFmpeg backend, batch processing, presets. Roadmap targets hardware acceleration, richer preset library, and workflow automation.

## Planned Features

### Format & Codec
- Hardware-accelerated encode paths (NVENC / QSV / AMF / VideoToolbox detection + selection)
- AV1 encode via SVT-AV1 with CRF and two-pass options
- HEVC/H.265 with x265 preset exposure
- HDR10/Dolby Vision passthrough + SDR tonemap fallback
- Image codecs: AVIF + JPEG XL encode (libavif, libjxl)
- Lossless re-mux mode (copy streams, just change container)

### Presets & Profiles
- "Discord 25MB" / "iPhone MP3 128k" / "Web WebP 1080" type quick presets
- User-saveable preset chain (crop → encode → strip-metadata) reusable across batches
- Import/export preset pack as JSON
- Recommended-preset auto-picker based on input probe (4K HDR → 1080p tonemap H.264 suggested)

### Batch Workflow
- Watch-folder mode: drop files into a folder, auto-convert per preset, move to output
- Resume interrupted batches (journal file per job)
- Parallelism slider (N concurrent FFmpeg processes)
- Progress aggregation: global ETA across a batch, not per-file only
- Conditional skip: "skip if output exists" / "skip if smaller than input"

### Audio Features
- Waveform preview on input
- Loudness normalization (EBU R128) as a checkbox
- Silence-trim auto-detect
- MusicBrainz tag lookup + embed on MP3/FLAC output

### Image Features
- Batch resize with aspect-ratio modes (fit / cover / pad)
- Watermark overlay (text or image, position + opacity)
- EXIF scrub toggle for privacy-conscious batches
- Automatic WebP/AVIF encode comparison (size + quality metrics)

### UX
- Drag-and-drop from Explorer / Finder
- Right-click Explorer shell integration ("Convert with MediaForge...")
- Compact mode for small-screen laptops
- PyInstaller single-exe distribution with bundled FFmpeg

## Competitive Research
- **HandBrake** — gold standard for video transcode; match preset philosophy but stay lighter.
- **FFmpeg Batch AV Converter** — dense UI, good for power users; lesson: expose raw ffmpeg args as escape hatch.
- **XnConvert** — batch image conversion leader; borrow its action-chain metaphor.
- **Shutter Encoder** — all-in-one Java tool with great codec coverage; reference for preset library size.

## Nice-to-Haves
- Cloud-queue mode: local GUI, remote worker runs the encode
- Plugin system for custom preset scripts (Python callable with input path, returns ffmpeg args)
- GPU vs CPU A/B benchmark tool built-in
- Metadata-only edit mode (rename, re-tag without re-encode)
- Encode-and-upload integrations (S3, Dropbox, SFTP post-hook)
- Color-grade LUT application (.cube files) during video encode

## Open-Source Research (Round 2)

### Related OSS Projects
- https://github.com/eibols/ffmpeg_batch — FFmpeg Batch AV Converter, drag-drop, pause/resume, encoding priority, auto-shutdown
- https://github.com/MattMcManis/Axiom — WPF FFmpeg GUI, script generator, lossless/VBR/CBR modes, aspect ratio presets
- https://github.com/HaveAGitGat/HBBatchBeast — HandBrake + FFmpeg multi-instance GUI, recursive folder scans, folder watching, Docker
- https://github.com/zbabac/VCT — Qt FFmpeg frontend, MP4↔MKV remux without re-encode (2min vs 2hr full transcode), manual command edit
- https://github.com/qwinff/qwinff — Qt FFmpeg GUI, preset library
- https://github.com/TuomoKu/SPX_Videotool — automated batch pipeline
- https://github.com/encode-gooey/EncodeGUI — AI-enhanced transcoder (upscale, interpolate, denoise via Real-ESRGAN / RIFE)

### Features to Borrow
- Folder-watch mode that auto-queues new files for conversion (HBBatchBeast) — valuable for MediaForge users processing camera dumps
- Drag-and-drop + pause/resume with encoding priority slider (ffmpeg_batch) — already have queue, add priority control
- Remux-only fast path (copy streams, change container) for MP4↔MKV↔MOV (VCT) — 50-100x faster than re-encode, huge UX win
- Command-script export — let users copy the generated ffmpeg command for reuse in scripts (Axiom) — educational + scriptable
- Multi-instance parallel encoding up to N CPUs (HBBatchBeast) — MediaForge currently serial, unlock throughput
- Auto-shutdown on batch complete (ffmpeg_batch) — overnight batch conversions
- AI upscaling pipeline integration: Real-ESRGAN + RIFE + Real-CUGAN as post-processing steps (EncodeGUI) — differentiator vs every other FFmpeg GUI
- Preset library with community-shareable JSON format (QWinFF) — publish to a preset repo

### Patterns & Architectures Worth Studying
- FFprobe → encoding options inference (Axiom) — read input streams and auto-pick codec/bitrate targets instead of requiring manual config
- Subtitle burn-in vs track embed dual path in same queue (ffmpeg_batch)
- Stream manipulation + multiplexing graph UI (ffmpeg_batch) — drag streams between input and output containers
- Per-file command override inside a batch (VCT) — user can hand-tweak one file without losing queue context
- HandBrake + FFmpeg dual-engine selection at job level (HBBatchBeast) — HandBrake for MP4/MKV presets, FFmpeg for everything else
