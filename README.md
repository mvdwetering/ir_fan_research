# IR Fan Research

This repository tracks my investigation into the infrared (IR) protocol used by my ceiling fan and related remotes. The goal is to understand the signal format well enough to control or automate the fan from Home Assistant.

The work includes captured signals, Pronto Hex recordings, photographs, PCB observations, datasheets, and notes on related remote designs and protocol implementations. Findings may still be incomplete; check the source captures and the device-specific notes when relying on them.

My ceiling fan is called "Ceilingfan Emanuel" (not even a proper brand).

## Background

I started this project years ago and initially tried to measure the signals directly from the original remote. That attempt damaged the remote, so the project stalled for a while. Later, I gathered IR captures with ESPHome on an ESP8266 board and eventually revisited the analysis with a Seeed Studio XIAO IR Mate.

Home Assistant 2026.4.0 added support for IR entities, which gave the project a new push. After flashing an ESPHome configuration that included an IR receiver component with logging, I captured the signals and discovered they did not match a standard protocol. ESPHome identified them as "SYMPHONY", but the payload looked like `C00` for every button — a false-positive clue rather than a real protocol break. The Pronto code output was more useful for deeper analysis.

## Current findings

The captured remotes use a protocol commonly referred to as **Symphony**, with two variants. In the "XIN HUI" variant found in the Emanuel and Madeira controllers, a message begins with `0x00` and `0x7F` frames, followed by repeated frames for the pressed button. Other researched devices appear to use the SM5021 variant.

The protocol seems to define only 8 commands, called K1 to K8. The meaning depends on the remote control and receiver. For example, the AA2 remote that came with my Emanuel fan maps K2 to Light Off, while the Madeira AA3 remote labels K2 as Light 2H. Sending K2 from the Madeira remote to my ceiling fan still results in the Light Off command.

See [ir_protocol/](ir_protocol/) for the decoding analysis and [research/](research/) for the device-specific findings.

## Repository contents

- [`decode_ir_messages.py`](decode_ir_messages.py) — decodes ESPHome raw logs, Pronto Hex captures, or raw CSV timing data and reports frame and timing details.
- [`legacy_remote_raw_analyzer.py`](legacy_remote_raw_analyzer.py) — an older helper for exploring timing clusters in ESPHome `remote.raw` output; kept mainly for historical reference.
- [`ir_protocol/`](ir_protocol/) — protocol analysis, frame layout, timing, and command observations.
- [`research/`](research/) — device-specific research, including signal captures, product photos, datasheets, and notes. Start at [research/README.md](research/README.md).

## The scripts

### `legacy_remote_raw_analyzer.py`

This script was used to understand the raw timing structure in the initial investigation. It is mainly kept here for historical documentation.

### `decode_ir_messages.py`

This script decodes raw IR data or Pronto captures using the protocol knowledge developed during the project. It also reports useful statistics and frame details. It was generated iteratively and is useful, but should still be treated critically.

## Typical message

This is a representative XIN HUI message from the decoder output:

```text
Message 19:
  Frames: 6
  Decodable: yes
  Variant: XIN HUI
  Custom code: 00 (0x0)
  Commands: K1 x4
  Bit time us: 1710.0
  Interframe gap us: n=6 min=6112.0 max=6167.0 mean=6122.5 stdev=19.9
  Interframe gap bits: n=6 min=3.57 max=3.61 mean=3.58 stdev=0.01
  Frame 01: 110000000000 | header=110 custom=00 control=0x00 (0000000) gap=6167.0us (3.61 bits) -> START_A
  Frame 02: 110001111111 | header=110 custom=00 control=0x7F (1111111) gap=6114.0us (3.58 bits) -> START_B
  Frame 03: 110000000001 | header=110 custom=00 control=0x01 (0000001) gap=6112.0us (3.57 bits) -> K1
  Frame 04: 110000000001 | header=110 custom=00 control=0x01 (0000001) gap=6114.0us (3.58 bits) -> K1
  Frame 05: 110000000001 | header=110 custom=00 control=0x01 (0000001) gap=6113.0us (3.57 bits) -> K1
  Frame 06: 110000000001 | header=110 custom=00 control=0x01 (0000001) gap=6115.0us (3.58 bits) -> K1
```

## Products and related notes

More details are available in the research directory.

Products that use the XIN HUI variant:

Products I own:

- "Emanuel" — ceiling fan from lampen24.nl (2020), has AA2 remote model.
- "Madeira" — IR fan controller from Hornbach used with Madeira ceiling fans, has AA3 remote model

Products that likely use the same protocol based on the captured data:

- DD2 remote
- Lindby remote (this seems to be the AA1 model)

Products that appear to use the SM5021 variant of the Symphony protocol based on the data I found:

- Symphony Air Cooler 3Di
- Blyss Owen-SW-5 3-speed fan with water mist
- Blyss WP-YK8 090218 Owen-SW-5 fan with water mist remote
- Westinghouse unknown ceiling fan with lights
- Westinghouse 78095 ceiling fan remote
- Satellite Electronic ID6 ceiling fan remote
- SilverCrest Lidl misting pedestal fan / SSVS 85 A1
- Vornado Transom

Each device or related project has its own notes in [research/](research/).
