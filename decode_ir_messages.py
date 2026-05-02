#!/usr/bin/env python3
"""Decode ceiling fan IR messages from ESPHome raw logs or raw Pronto data.

This script decodes 12-bit frames where each bit is encoded as:
- 1 => long mark + short space
- 0 => short mark + long space

It supports two input formats:
1) ESPHome debug logs containing lines like: "Received Raw: ..."
2) Raw Pronto Hex (type 0000)
"""

from __future__ import annotations

import argparse
import collections
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

# Protocol constants derived from repository notes.
FRAME_BITS = 12
EXPECTED_HEADER = "110"
SUPPORTED_HEADERS = {"110", "010"}
LABEL_COLUMN_WIDTH = 7

NAME_LABELS = {
    "110000000000": "START_A",
    "110001111111": "START_B",
}

COMMAND_MAP = {
    0x01: "K1",
    0x02: "K2",
    0x04: "K3",
    0x08: "K4",
    0x10: "K5",
    0x20: "K6",
    0x43: "K7",
    0x46: "K8",
}


@dataclass
class Thresholds:
    mark_short: float
    mark_long: float
    mark_threshold: float
    space_short: float
    space_long: float
    space_threshold: float
    gap_threshold: float
    gap_estimate: float


@dataclass
class Frame:
    bits: str
    header: str
    custom_bits: str
    control_word: int
    label: str
    key: str | None = None


@dataclass
class MessageDecode:
    index: int
    frame_count: int
    frames: List[Frame]
    warnings: List[str] = field(default_factory=list)
    custom_code: str | None = None
    frame_gap_us: List[float | None] = field(default_factory=list)
    frame_gap_bits: List[float | None] = field(default_factory=list)
    frame_gap_outlier: List[bool] = field(default_factory=list)
    interframe_gaps_us: List[float] = field(default_factory=list)
    interframe_gaps_bits: List[float] = field(default_factory=list)
    bit_time_us: float = 0.0
    is_decodable: bool = False
    variant: str | None = None


def split_low_high(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return float(values[0]), float(values[0])

    mid = statistics.median(values)
    low = [v for v in values if v <= mid]
    high = [v for v in values if v > mid]

    if not low:
        low = [min(values)]
    if not high:
        high = [max(values)]

    return float(statistics.median(low)), float(statistics.median(high))


def compute_thresholds(message: Sequence[int], gap_floor_us: int) -> Thresholds:
    marks = [abs(message[i]) for i in range(0, len(message), 2)]
    spaces = [abs(message[i]) for i in range(1, len(message), 2)]

    # Data spaces are around short/long symbol spaces; long values contain interframe gap.
    data_spaces = [s for s in spaces if s < gap_floor_us]
    if not data_spaces:
        data_spaces = spaces

    mark_short, mark_long = split_low_high(marks)
    space_short, space_long = split_low_high(data_spaces)

    long_spaces = [s for s in spaces if s >= gap_floor_us]
    if long_spaces:
        # A bit below the smallest observed long space separates normal data spaces
        # from spaces that include interframe silence.
        gap_threshold = max(float(gap_floor_us), min(long_spaces) * 0.8)
        gap_estimate = max(
            0.0,
            float(statistics.median(long_spaces)) - ((space_short + space_long) / 2.0),
        )
    else:
        gap_threshold = max(float(gap_floor_us), space_long * 2.0)
        gap_estimate = 0.0

    return Thresholds(
        mark_short=mark_short,
        mark_long=mark_long,
        mark_threshold=(mark_short + mark_long) / 2.0,
        space_short=space_short,
        space_long=space_long,
        space_threshold=(space_short + space_long) / 2.0,
        gap_threshold=gap_threshold,
        gap_estimate=gap_estimate,
    )


def classify_bit(mark_us: int, space_us: int, t: Thresholds) -> tuple[str, str | None]:
    mark_abs = abs(mark_us)
    space_abs = abs(space_us)

    mark_bit = 1 if mark_abs >= t.mark_threshold else 0

    # Compensate interframe silence that gets appended to the last bit space.
    if space_abs >= t.gap_threshold and t.gap_estimate > 0:
        space_comp = max(0.0, space_abs - t.gap_estimate)
    else:
        space_comp = float(space_abs)

    # For normal spaces: short => 1, long => 0.
    space_bit = 1 if space_comp <= t.space_threshold else 0

    # Use a two-hypothesis score to reduce boundary errors.
    score_1 = abs(mark_abs - t.mark_long) + abs(space_comp - t.space_short)
    score_0 = abs(mark_abs - t.mark_short) + abs(space_comp - t.space_long)
    bit_value = 1 if score_1 < score_0 else 0

    warning = None
    if mark_bit != space_bit:
        warning = (
            f"mark/space mismatch (mark={mark_abs}us, space={space_abs}us, "
            f"mark_bit={mark_bit}, space_bit={space_bit})"
        )

    return str(bit_value), warning


def decode_frame_bits(bits: str) -> Frame:
    header = bits[:3]
    custom_bits = bits[3:5]
    control_bits = bits[5:]
    control_word = int(control_bits, 2)

    key = None
    label = NAME_LABELS.get(bits)
    if label is None:
        label = "COMMAND"
        key = COMMAND_MAP.get(control_word, "UNKNOWN_COMMAND")

    return Frame(
        bits=bits,
        header=header,
        custom_bits=custom_bits,
        control_word=control_word,
        label=label,
        key=key,
    )


def decode_message(message: Sequence[int], index: int, gap_floor_us: int) -> MessageDecode:
    warnings: List[str] = []
    frames: List[Frame] = []
    bit_buffer: List[str] = []
    interframe_gaps_us: List[float] = []
    bit_durations_us: List[float] = []
    frame_gap_us: List[float | None] = []

    t = compute_thresholds(message, gap_floor_us=gap_floor_us)

    pair_count = len(message) // 2
    for pair_idx in range(pair_count):
        mark = message[2 * pair_idx]
        space = message[2 * pair_idx + 1]

        bit, warning = classify_bit(mark, space, t)
        bit_buffer.append(bit)
        if warning:
            warnings.append(f"pair {pair_idx + 1}: {warning}")

        frame_end = abs(space) >= t.gap_threshold or len(bit_buffer) >= FRAME_BITS
        if frame_end:
            if len(bit_buffer) == FRAME_BITS:
                frame_bits = "".join(bit_buffer)
                frames.append(decode_frame_bits(frame_bits))
                if abs(space) >= t.gap_threshold:
                    expected_data_space = t.space_short if bit == "1" else t.space_long
                    effective_gap = max(0.0, abs(space) - expected_data_space)
                    interframe_gaps_us.append(effective_gap)
                    frame_gap_us.append(effective_gap)
                else:
                    frame_gap_us.append(None)
                    bit_durations_us.append(abs(mark) + abs(space))
            else:
                warnings.append(
                    f"partial frame ended with {len(bit_buffer)} bits at pair {pair_idx + 1}"
                )
            bit_buffer = []

    if bit_buffer:
        warnings.append(f"trailing partial frame with {len(bit_buffer)} bits")

    custom_code = None
    custom_candidates = [f.custom_bits for f in frames if f.header in SUPPORTED_HEADERS]
    if custom_candidates:
        # The fan protocol uses a constant 2-bit custom code across a message.
        common = collections.Counter(custom_candidates).most_common(1)[0][0]
        custom_code = common

    if bit_durations_us:
        bit_time_us = float(statistics.median(bit_durations_us))
    else:
        bit_time_us = (t.mark_short + t.space_long + t.mark_long + t.space_short) / 2.0

    frame_gap_bits: List[float | None]
    if bit_time_us > 0:
        interframe_gaps_bits = [gap / bit_time_us for gap in interframe_gaps_us]
        frame_gap_bits = [gap / bit_time_us if gap is not None else None for gap in frame_gap_us]
    else:
        interframe_gaps_bits = []
        frame_gap_bits = [None for _ in frame_gap_us]

    non_null_frame_gaps = [g for g in frame_gap_us if g is not None]
    if non_null_frame_gaps:
        gap_median = float(statistics.median(non_null_frame_gaps))
        deviations = [abs(g - gap_median) for g in non_null_frame_gaps]
        gap_mad = float(statistics.median(deviations))
        # Mark as weird if far from message-typical gap; floor avoids over-sensitivity.
        outlier_threshold = max(500.0, gap_mad * 3.0)
        frame_gap_outlier = [
            (g is not None and abs(g - gap_median) > outlier_threshold) for g in frame_gap_us
        ]
    else:
        frame_gap_outlier = [False for _ in frame_gap_us]

    command_count = sum(1 for f in frames if f.label == "COMMAND")
    unknown_count = sum(1 for f in frames if f.label in {"UNKNOWN_HEADER", "UNKNOWN_COMMAND"})
    has_expected_start_frames = (
        len(frames) >= 2
        and frames[0].label == "START_A"
        and frames[1].label == "START_B"
    )
    # Bare variant: only COMMAND frames, no start frames at all.
    has_no_start_frames = all(f.label not in {"START_A", "START_B"} for f in frames)
    is_decodable = command_count > 0 and unknown_count == 0 and (
        has_expected_start_frames or has_no_start_frames
    )
    if is_decodable:
        variant: str | None = "XIN HUI" if has_expected_start_frames else "SM5021"
    else:
        variant = None

    return MessageDecode(
        index=index,
        frame_count=len(frames),
        frames=frames,
        warnings=warnings,
        custom_code=custom_code,
        frame_gap_us=frame_gap_us,
        frame_gap_bits=frame_gap_bits,
        frame_gap_outlier=frame_gap_outlier,
        interframe_gaps_us=interframe_gaps_us,
        interframe_gaps_bits=interframe_gaps_bits,
        bit_time_us=bit_time_us,
        is_decodable=is_decodable,
        variant=variant,
    )


def parse_esphome_messages(text: str, min_pairs: int) -> List[List[int]]:
    messages: List[List[int]] = []
    current: List[int] | None = None

    for line in text.splitlines():
        start_match = re.search(r"remote\.raw:\d+\]:\s*Received Raw:(.*)$", line)
        if start_match:
            payload = start_match.group(1)
            values = [int(x) for x in re.findall(r"-?\d+", payload)]
            if not values:
                continue
            if current is not None:
                messages.append(current)
            current = values
            continue

        # Wrapped logger continuations for the same raw message may omit
        # "Received Raw:" and only keep comma-separated timings.
        cont_match = re.search(r"remote\.raw:\d+\]:(.*)$", line)
        if cont_match and current is not None and "Received Raw:" not in line:
            payload = cont_match.group(1)
            values = [int(x) for x in re.findall(r"-?\d+", payload)]
            if values:
                current.extend(values)

    if current is not None:
        messages.append(current)

    cleaned: List[List[int]] = []
    for msg in messages:
        # A valid raw IR frame must start with a mark (positive duration).
        # If it starts with a negative value, the capture begins mid-frame and is invalid.
        if not msg or msg[0] < 0:
            continue
        # Keep only complete mark/space pairs.
        if len(msg) % 2 == 1:
            msg = msg[:-1]
        if len(msg) // 2 < min_pairs:
            continue
        # Ignore tiny jitter/noise captures (typical noise sits around ~60-200us).
        if max(abs(v) for v in msg) < 500:
            continue
        cleaned.append(msg)

    return cleaned


def parse_pronto_messages(text: str) -> List[List[int]]:
    tokens = [int(x, 16) for x in re.findall(r"\b[0-9A-Fa-f]{4}\b", text)]
    messages: List[List[int]] = []

    i = 0
    while i + 3 < len(tokens):
        if tokens[i] != 0x0000:
            i += 1
            continue

        freq_word = tokens[i + 1]
        burst_pairs = tokens[i + 2]
        repeat_pairs = tokens[i + 3]
        timing_count = (burst_pairs + repeat_pairs) * 2

        if freq_word <= 0 or timing_count <= 0:
            i += 1
            continue

        start = i + 4
        end = start + timing_count
        if end > len(tokens):
            break

        # Pronto timing unit is freq_word * 0.241246 us.
        unit_us = freq_word * 0.241246
        msg: List[int] = []
        for j, count in enumerate(tokens[start:end]):
            dur = int(round(count * unit_us))
            msg.append(dur if j % 2 == 0 else -dur)

        messages.append(msg)
        i = end

    return messages


def _is_label_line(line: str) -> bool:
    """Return True if the line is a text label rather than timing data.

    A label line starts with a letter and contains no comma.
    """
    stripped = line.strip()
    return bool(stripped) and stripped[0].isalpha() and "," not in stripped


def _parse_rawcsv_line(values: List[int], gap_floor_us: int, min_pairs: int) -> List[List[int]]:
    """Split a flat list of timing values into messages on interframe gaps."""
    messages: List[List[int]] = []
    current: List[int] = []
    for v in values:
        is_mark_position = (len(current) % 2 == 0)
        if v >= gap_floor_us and is_mark_position and current:
            # Large value on a mark slot => end of the previous segment.
            if len(current) % 2 == 1:
                current = current[:-1]
            if len(current) // 2 >= min_pairs:
                messages.append(current)
            current = [v]
        else:
            current.append(v)
    if current:
        if len(current) % 2 == 1:
            current = current[:-1]
        if len(current) // 2 >= min_pairs:
            messages.append(current)
    return messages


def parse_rawcsv_messages(text: str, gap_floor_us: int, min_pairs: int) -> List[List[int]]:
    """Parse comma/whitespace separated timing values into messages.

    The text is split into capture blocks: a blank line or a label line (one
    that starts with a letter and contains no comma) ends the current block and
    starts a new one.  Consecutive timing lines within the same block are
    concatenated before parsing so that multi-line captures are handled
    correctly.  The block boundary also resets the mark/space alignment, so an
    odd-length line in one capture does not corrupt the next one.
    """
    messages: List[List[int]] = []
    current_values: List[int] = []

    def flush() -> None:
        if current_values:
            messages.extend(_parse_rawcsv_line(current_values, gap_floor_us, min_pairs))
            current_values.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _is_label_line(line):
            flush()
        else:
            current_values.extend(int(x) for x in re.findall(r"\d+", line))

    flush()
    return messages


def detect_input_type(text: str) -> str:
    if "Received Raw:" in text:
        return "esphome"
    if re.search(r"\b0000\b", text) and re.search(r"\b[0-9A-Fa-f]{4}\b", text):
        return "pronto"
    # Plain numbers only, or labeled capture file where some lines are text
    # labels and the rest are comma-separated timing values.
    has_number_line = any(
        re.search(r"\d+\s*,\s*\d+", line) for line in text.splitlines()
    )
    if has_number_line:
        return "rawcsv"
    raise ValueError("Could not detect input type. Use --input-type to specify.")


def summarize_commands(frames: Iterable[Frame]) -> str:
    counts: dict[str, int] = {}
    for frame in frames:
        if frame.key:
            counts[frame.key] = counts.get(frame.key, 0) + 1

    if not counts:
        return "none"

    parts = [f"{name} x{count}" for name, count in sorted(counts.items())]
    return ", ".join(parts)


def print_results(results: Sequence[MessageDecode], source: str, show_warnings: bool) -> None:
    if not results:
        print("No decodable messages found.")
        return

    print(f"Decoded {len(results)} message(s) from {source} input.")
    all_gaps_us: List[float] = []
    all_gaps_bits: List[float] = []
    for res in results:
        print()
        print(f"Message {res.index}:")
        print(f"  Frames: {res.frame_count}")
        print(f"  Decodable: {'yes' if res.is_decodable else 'no'}")
        if res.variant:
            print(f"  Variant: {res.variant}")
        if res.custom_code:
            print(f"  Custom code: {res.custom_code} (0x{int(res.custom_code, 2):X})")
        print(f"  Commands: {summarize_commands(res.frames)}")
        print(f"  Bit time us: {res.bit_time_us:.1f}")
        if res.interframe_gaps_us:
            if len(res.interframe_gaps_us) >= 2:
                msg_stdev_us = statistics.pstdev(res.interframe_gaps_us)
            else:
                msg_stdev_us = 0.0
            print(
                "  Interframe gap us: "
                f"n={len(res.interframe_gaps_us)} "
                f"min={min(res.interframe_gaps_us):.1f} "
                f"max={max(res.interframe_gaps_us):.1f} "
                f"mean={statistics.mean(res.interframe_gaps_us):.1f} "
                f"stdev={msg_stdev_us:.1f}"
            )
            if res.interframe_gaps_bits:
                if len(res.interframe_gaps_bits) >= 2:
                    msg_stdev_bits = statistics.pstdev(res.interframe_gaps_bits)
                else:
                    msg_stdev_bits = 0.0
                print(
                    "  Interframe gap bits: "
                    f"n={len(res.interframe_gaps_bits)} "
                    f"min={min(res.interframe_gaps_bits):.2f} "
                    f"max={max(res.interframe_gaps_bits):.2f} "
                    f"mean={statistics.mean(res.interframe_gaps_bits):.2f} "
                    f"stdev={msg_stdev_bits:.2f}"
                )
            if res.is_decodable:
                all_gaps_us.extend(res.interframe_gaps_us)
                all_gaps_bits.extend(res.interframe_gaps_bits)
        else:
            print("  Interframe gap us: n=0")
            print("  Interframe gap bits: n=0")

        for idx, frame in enumerate(res.frames, start=1):
            control_bin = format(frame.control_word, "07b")
            tail = (
                f"header={frame.header} custom={frame.custom_bits} "
                f"control=0x{frame.control_word:02X} ({control_bin})"
            )
            if idx - 1 < len(res.frame_gap_us) and res.frame_gap_us[idx - 1] is not None:
                gap_us = res.frame_gap_us[idx - 1]
                gap_bits = res.frame_gap_bits[idx - 1]
                tail += f" gap={gap_us:.1f}us"
                if gap_bits is not None:
                    tail += f" ({gap_bits:.2f} bits)"
                if idx - 1 < len(res.frame_gap_outlier) and res.frame_gap_outlier[idx - 1]:
                    tail += " OUTLIER_GAP"
            if frame.key:
                tail += f" -> {frame.key}"
            label_text = frame.label.ljust(LABEL_COLUMN_WIDTH)
            print(f"  Frame {idx:02d}: {frame.bits} | {label_text} | {tail}")

        if show_warnings and res.warnings:
            print("  Warnings:")
            for warning in res.warnings[:20]:
                print(f"    - {warning}")
            if len(res.warnings) > 20:
                print(f"    - ... {len(res.warnings) - 20} more")

    if all_gaps_us:
        if len(all_gaps_us) >= 2:
            global_stdev_us = statistics.pstdev(all_gaps_us)
        else:
            global_stdev_us = 0.0
        if len(all_gaps_bits) >= 2:
            global_stdev_bits = statistics.pstdev(all_gaps_bits)
        else:
            global_stdev_bits = 0.0
        print()
        print("Global interframe gap summary (decodable messages only):")
        print(
            "  us: "
            f"n={len(all_gaps_us)} "
            f"min={min(all_gaps_us):.1f} "
            f"max={max(all_gaps_us):.1f} "
            f"mean={statistics.mean(all_gaps_us):.1f} "
            f"stdev={global_stdev_us:.1f}"
        )
        print(
            "  bits: "
            f"n={len(all_gaps_bits)} "
            f"min={min(all_gaps_bits):.2f} "
            f"max={max(all_gaps_bits):.2f} "
            f"mean={statistics.mean(all_gaps_bits):.2f} "
            f"stdev={global_stdev_bits:.2f}"
        )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Decode fan IR protocol frames from ESPHome raw logs or raw Pronto captures."
        )
    )
    parser.add_argument(
        "input",
        help="Path to input file or '-' to read from stdin.",
    )
    parser.add_argument(
        "--input-type",
        choices=["auto", "esphome", "pronto", "rawcsv"],
        default="auto",
        help="Input format. Defaults to auto detection.",
    )
    parser.add_argument(
        "--min-pairs",
        type=int,
        default=12,
        help="Minimum mark/space pairs for ESPHome messages (default: 12).",
    )
    parser.add_argument(
        "--gap-floor-us",
        type=int,
        default=3000,
        help="Minimum space duration that may indicate interframe gap (default: 3000).",
    )
    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="Print decode warnings.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    if args.input == "-":
        text = sys.stdin.read()
        source_name = "stdin"
    else:
        p = Path(args.input)
        text = p.read_text(encoding="utf-8", errors="ignore")
        source_name = str(p)

    input_type = args.input_type
    if input_type == "auto":
        input_type = detect_input_type(text)

    if input_type == "esphome":
        messages = parse_esphome_messages(text, min_pairs=args.min_pairs)
    elif input_type == "pronto":
        messages = parse_pronto_messages(text)
    else:
        messages = parse_rawcsv_messages(text, gap_floor_us=args.gap_floor_us, min_pairs=args.min_pairs)

    results = [
        decode_message(msg, index=i + 1, gap_floor_us=args.gap_floor_us)
        for i, msg in enumerate(messages)
    ]

    print_results(results, source=f"{input_type} ({source_name})", show_warnings=args.show_warnings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
