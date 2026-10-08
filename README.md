# IR Fan Research

This repository documents the investigation of infrared (IR) remotes used by ceiling fans and related appliances. The goal is to identify compatible products, understand their IR protocols, and make it possible to control a fan from Home Assistant.

The research includes captured signals, Pronto Hex files, photographs, PCB observations, datasheets, and notes about related remotes and protocol implementations. Findings are empirical and may be incomplete; check the source captures and individual research notes when relying on them.

## Current findings

The captured remotes use a protocol identified as **Symphony**, with differences between variants. In the XIN HUI variant found in the Emanuel and Madeira research, a message begins with `0x00` and `0x7F` frames, followed by repeated frames for the pressed button. Other researched devices appear to use the SM5021 variant. These are investigation results, not a claim that every product listed is compatible.

See [IR protocol notes](ir_protocol/) for the decoding analysis and [research notes](research/) for device-specific evidence.

## Repository contents

- [`decode_ir_messages.py`](decode_ir_messages.py) — decodes ESPHome raw logs, Pronto Hex captures, or raw CSV timing data and reports frame and timing details.
- [`legacy_remote_raw_analyzer.py`](legacy_remote_raw_analyzer.py) — an older helper for exploring timing clusters in ESPHome `remote.raw` output; kept mainly for historical reference.
- [`ir_protocol/`](ir_protocol/) — protocol analysis, frame layout, timing, and command observations.
- [`research/`](research/) — device and implementation research, including signal captures, product photos, and datasheets. Start at its [index](research/index.md).

## Decode captures

The scripts use only the Python standard library; Python 3 is required. No package installation is needed.

Decode a capture file with automatic input-format detection:

```sh
python3 decode_ir_messages.py path/to/capture.txt
```

Choose a format explicitly when automatic detection is not appropriate:

```sh
python3 decode_ir_messages.py path/to/capture.txt --input-type esphome
python3 decode_ir_messages.py path/to/capture.pronto --input-type pronto
python3 decode_ir_messages.py path/to/capture.csv --input-type rawcsv
```

The decoder also accepts standard input by using `-` as the input path:

```sh
cat path/to/capture.txt | python3 decode_ir_messages.py -
```

Run `python3 decode_ir_messages.py --help` for all options. The legacy analyzer accepts an ESPHome log file and can either suggest timing clusters or classify timings using supplied spacing values:

```sh
python3 legacy_remote_raw_analyzer.py path/to/capture.log
python3 legacy_remote_raw_analyzer.py path/to/capture.log --spacing short,long,space
```

## Research areas

Each device or related project has its own notes in `research/`. Current topics include the Emanuel and Madeira fans/controllers, a DD2 ceiling fan remote, Lindby, Vornado Transom, Symphony/SM5021 remotes, and work associated with the IrRemoteESP8266 project. Refer to each area's notes for what was actually captured or confirmed.

## Using the captures

The signal files are research artifacts, not a ready-made Home Assistant integration. IR compatibility can depend on the exact remote, receiver, protocol variant, and command; verify behavior with the device you intend to control.
