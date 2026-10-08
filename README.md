# IR Fan Research

This repository documents the investigation of infrared (IR) remotes used by my ceiling fan and others. The goal is to understand the IR protocol.

The research includes captured signals, Pronto Hex files, photographs, PCB observations, datasheets, and notes about related remotes and protocol implementations. Findings are empirical and may be incomplete; check the source captures and individual research notes when relying on them.

## Current findings

The captured remotes use a protocol commonly referred to as **Symphony**, with differences between variants. In the XIN HUI variant found in the Emanuel and Madeira research, a message begins with `0x00` and `0x7F` frames, followed by repeated frames for the pressed button. Other researched devices appear to use the SM5021 variant. These are investigation results, not a claim that every product listed is compatible.

See [IR protocol notes](ir_protocol/) for the decoding analysis and [research notes](research/) for device-specific evidence.

## Repository contents

- [`decode_ir_messages.py`](decode_ir_messages.py) — decodes ESPHome raw logs, Pronto Hex captures, or raw CSV timing data and reports frame and timing details.
- [`legacy_remote_raw_analyzer.py`](legacy_remote_raw_analyzer.py) — an older helper for exploring timing clusters in ESPHome `remote.raw` output; kept mainly for historical reference.
- [`ir_protocol/`](ir_protocol/) — protocol analysis, frame layout, timing, and command observations.
- [`research/`](research/) — device and implementation research, including signal captures, product photos, and datasheets. Start at its [index](research/index.md).

## Research areas

Each device or related project has its own notes in `research/`. Current topics include the Emanuel and Madeira fans/controllers, a DD2 ceiling fan remote, Lindby, Vornado Transom, Symphony/SM5021 remotes, and work associated with the IrRemoteESP8266 project. Refer to each area's notes for what was actually captured or confirmed.
