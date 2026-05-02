# IR protocol

## TL;DR

## Reverse engineering the protocol (the journey)

(this is the result of some back and forth with AI, I believe the outcome is correct but the story needs some cleanup due to weird phrasings and some parts have not been fully update after new findings were done)

All eight button presses were captured with an IR receiver, saved in Pronto Hex
format, and decoded with a Python script
([`analyze_ir_capture.py`](https://github.com/example/repo)).

---

## Pronto Hex captures

Pronto Hex is a widely used representation for raw IR signals. The first four
16-bit words are a header:

```text
[type] [freq_word] [burst_pairs] [repeat_pairs]  [mark0 space0 mark1 space1 ...]
```

* **type** `0x0000` — raw, unmodulated format (timing stored as counts)
* **freq_word** — carrier period in units of 0.241 246 µs; `0x006D` = 109 → 38.03 kHz
* **burst_pairs** — number of mark/space pairs that follow
* **repeat_pairs** — `0x0000` here (repeat frame is empty; the device handles its own repetition)

All eight captures share `0000 006D`, confirming a single carrier and a single
IC design driving both brands.

### HI

```text
0000 006D 0054 0000
0031 0010 0030 0010 0011 0030 0011 002F 0012 002F 0011 0030 0011 0030 0011 0030
0010 0030 0010 0030 0010 0031 0010 011C 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 00FC
0030 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0030 00FC 0030 0010 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0032 000F 0031 002F 00FD
002F 0011 002F 0012 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032
000F 0032 000F 0032 000F 0032 002F 00FD 002F 0011 002F 0012 000F 0032 000F 0032
000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 002E 00FD
002F 0011 0030 0011 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032
000F 0032 000F 0032 000F 0032 0030 09D8
```

### MED

```text
0000 006D 0060 0000
0032 0010 0030 0010 0011 0030 0012 002F 0011 0030 0011 0030 0011 0031 0010 0031
0010 0031 0010 0030 0010 0031 0010 011C 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 00FC
0030 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031
0010 0031 0031 0010 0010 0031 0010 011C 0030 0010 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0031 0010 0010 0031 0010 011C
0030 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0032
000F 0032 0030 0011 000F 0032 000F 011D 002F 0011 002F 0012 000F 0032 000F 0032
000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 0030 0011 000F 0032 000F 011D
002F 0011 002F 0012 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032
000F 0032 0030 0011 000F 0032 000F 011D 002F 0011 002F 0012 000F 0032 000F 0032
000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 002F 0012 000F 0032 000F 09D8
```

### LOW

```text
0000 006D 0048 0000
0032 0010 002F 0010 0011 0030 0011 0030 0012 002F 0012 002F 0011 0030 0011 0030
0010 0030 0010 0031 0010 0030 0010 011C 0031 0010 0031 0010 0010 0031 0010 0031
0010 0031 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 00FB
0030 0010 0031 0010 0010 0031 0010 0031 0010 0031 0031 0010 0010 0031 0010 0031
0010 0031 0010 0031 0030 0011 0030 00FC 0030 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0030 0011 0030 00FC
0030 0010 0030 0011 0010 0031 0010 0031 0010 0031 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0031 0010 0031 00FB 0030 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0030 0010 0031 09D8
```

### OFF

```text
0000 006D 0054 0000
0032 000F 0030 000F 0011 0030 0011 002F 0012 002E 0012 002F 0011 0030 0011 0030
0010 0031 0010 0031 0010 0031 0010 011D 0031 0010 0030 0010 0010 0031 0010 0031
0010 0031 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0030 00FC
0031 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0030 0010
0010 0031 0010 0031 0010 0031 0010 011D 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0030 0011 0010 0031 0010 0031 0010 0031 0010 011D
0031 0010 0031 0010 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0030 0011
0010 0031 0010 0031 0010 0031 0010 011D 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0031 0010 0010 0031 0010 0031 0010 0031 0010 011C
0030 0010 0031 0010 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0030 0011
0010 0031 0010 0031 0010 0031 0010 09D8
```

### ON/OFF

```text
0000 006D 0054 0000
0030 0011 0030 000F 0011 0030 0012 002E 0012 002F 0011 0030 0011 0030 0010 0031
0010 0030 0010 0030 0010 0031 0010 0110 0030 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 00FB
0031 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031
0030 0011 0010 0031 0010 0031 0010 0110 0030 0011 0031 0010 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0010 0031 0031 0010 0010 0031 0010 0031 0010 0110
0030 0012 002F 0012 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032
002F 0012 000F 0032 000F 0032 000F 0111 002F 0012 002F 0012 000F 0032 000F 0032
000F 0032 000F 0032 000F 0032 000F 0032 002F 0012 000F 0032 000F 0032 000F 011E
002F 0011 002F 0011 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032 000F 0032
0030 0011 000F 0032 000F 0032 000F 09D8
```

### 2H

```text
0000 006D 0054 0000
0032 000F 0030 0010 0012 002E 0011 002F 0011 0030 0011 0031 0010 0030 0010 0031
0010 0030 0010 0031 0010 0031 0010 0110 0030 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 00FB
0031 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0030 0011 0010 0031
0010 0031 0010 0031 0010 0031 0010 0110 0030 0010 0031 0010 0010 0031 0010 0031
0010 0031 0010 0031 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0110
0030 0011 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0031 0010 0010 0031
0010 0031 0010 0031 0010 0031 0010 0110 0030 0011 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 011D
0030 0010 0031 0010 0010 0031 0010 0031 0010 0031 000F 0032 002F 0011 0010 0031
0010 0032 000F 0032 000F 0032 000F 09D8
```

### 4H

```text
0000 006D 003C 0000
0032 000F 002F 0010 0011 0030 0011 002F 0012 002F 0012 002F 0011 0030 0010 0031
0010 0030 0010 0030 0010 0031 0010 011D 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 0011 0030 00FD
0031 0010 0030 0011 0010 0031 0010 0031 0010 0031 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0010 011D 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0010 0031 0010 0031 0010 0031 0030 0011 0030 0011 0010 011C
0030 0010 0030 0011 0010 0031 0010 0031 0010 0031 0030 0011 0010 0031 0010 0031
0010 0031 0030 0011 0030 0011 0010 09D8
```

### 8H

```text
0000 006D 003C 0000
0031 0010 0030 000F 0011 002F 0011 002F 0012 002E 0011 002F 0011 002F 0011 0030
0010 0031 0010 0030 0010 0030 0010 011D 0031 0010 0031 0010 0010 0031 0010 0031
0010 0031 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 00FC
0031 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031
0010 0031 0010 0031 0031 0010 0010 011D 0031 0010 0030 0011 0010 0031 0010 0031
0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0030 0011 0010 011C
0030 0010 0030 0011 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031
0010 0031 0010 0031 0031 0010 0010 09D8
```

---

### Carrier

All captures begin with `0000 006D`. The Pronto carrier period is:

$$T_{carrier} = 0x6D \times 0.241246\ \mu s = 109 \times 0.241246 \approx 26.30\ \mu s$$

$$f_{carrier} = \frac{1}{26.30\ \mu s} \approx 38.0\ \text{kHz}$$

This is the standard 38 kHz used by virtually all consumer IR remotes and is
compatible with common IR receiver ICs (TSOP4838, VS1838B, etc.).

### Bit encoding

The protocol uses **pulse-width modulation** (PWM), also called
mark-width encoding. Every bit occupies exactly the same total time
(`0x40` units ≈ 1683 µs); it is the **mark (on) length** that encodes the
bit value, while the space (off) is simply the complement:

| Mark value | Space value | Total | Duration (µs) | Bit |
|------------|-------------|-------|---------------|-----|
| ~`0x30`    | ~`0x10`     | `0x40`| ~1683         | 1   |
| ~`0x10`    | ~`0x30`     | `0x40`| ~1683         | 0   |

The 3:1 ratio between long and short intervals is consistent with
Japanese-appliance AEHA-style timing, though the encoding here is
mark-width rather than space-width.

The Pronto values in these captures sit in the raw format with **no AGC leader
burst**. The first mark/space pair is simply the first data symbol, which
confirms this is a bare proprietary format rather than NEC, RC-5, or RC-6.

---

## Frame structure

Each button press is a single Pronto Hex blob, but inside that blob there are
multiple logical **mini-frames** separated by long inter-frame gaps. Each
mini-frame contains exactly **12 mark/space pairs**, encoding **12 bits** of data.

A complete button press always follows the same three-part structure:

```text
[ PREAMBLE_A ] gap [ PREAMBLE_B ] gap [ COMMAND ] gap [ COMMAND ] gap ...
```

| Mini-frame | Bit pattern      | Payload (8-bit) | Role              |
|------------|------------------|-----------------|-------------------|
| Preamble A | `110000000000`   | `0x00`          | Constant — sync   |
| Preamble B | `110001111111`   | `0x7F`          | Constant — device |
| Command    | varies per key   | see table       | Button command    |

The command word is repeated three to six times depending on the button. This
is likely handled internally by the IC's firmware with no dependency on the
host's button-hold duration.

### Bit layout within each mini-frame

Each 12-bit word consists of:

```text
[ b11 b10 b9 b8 b7 b6 b5 b4 ] [ b3 b2 b1 b0 ]
  ^^^^^^^^ 8-bit payload ^^^^   ^^^^ prefix
```

The four most-significant bits are always `1100` for all frames observed. The
lower eight bits form the meaningful payload byte.

### Last-bit encoding

Every mini-frame ends with a 12th mark/space pair where the space value is
anomalously large because the inter-frame silence is appended directly to it:

$$s_{last} = s_{data} + s_{gap}$$

The inter-frame silence (`~0xEC` pronto units, **~6.2 ms**) is not a separate
token. To recover the 12th data bit, subtract the fixed gap and classify the
remainder by the normal PWM threshold:

$$\text{bit}_{12} = \begin{cases} 1 & m_{12} > \text{threshold} \\ 0 & \text{otherwise} \end{cases}$$

where $m_{12}$ is the mark of the 12th pair (unchanged by the gap) and the
threshold is the midpoint between short and long mark values.

The protocol is therefore **purely PWM throughout all 12 bits**.

---

## Command table

| PCB label | Button | Command word (12-bit) | Payload (8-bit) | Hex    | Binary        |
|-----------|--------|-----------------------|-----------------|--------|---------------|
| K1        | HI     | `110000000001`        | `00000001`      | `0x01` | `0000 0001`   |
| K2        | 8H     | `110000000010`        | `00000010`      | `0x02` | `0000 0010`   |
| K3        | MED    | `110000000100`        | `00000100`      | `0x04` | `0000 0100`   |
| K4        | ON/OFF | `110000001000`        | `00001000`      | `0x08` | `0000 1000`   |
| K5        | OFF    | `110000010000`        | `00010000`      | `0x10` | `0001 0000`   |
| K6        | 2H     | `110000100000`        | `00100000`      | `0x20` | `0010 0000`   |
| K7        | LOW    | `110001000011`        | `01000011`      | `0x43` | `0100 0011`   |
| K8        | 4H     | `110001000110`        | `01000110`      | `0x46` | `0100 0110`   |

### Pattern observation

Ordered by PCB label, the payload bytes reveal a clean sequential one-hot
pattern across K1–K6:

| PCB label | Button | Payload | Bit set (0 = LSB) |
|-----------|--------|---------|-------------------|
| K1        | HI     | `0x01`  | bit 0             |
| K2        | 8H     | `0x02`  | bit 1             |
| K3        | MED    | `0x04`  | bit 2             |
| K4        | ON/OFF | `0x08`  | bit 3             |
| K5        | OFF    | `0x10`  | bit 4             |
| K6        | 2H     | `0x20`  | bit 5             |
| K7        | LOW    | `0x43`  | bits 0+1+6        |
| K8        | 4H     | `0x46`  | bits 1+2+6        |

K1–K6 map to exactly one bit each, in ascending order. The protocol uses
**active-high one-hot** encoding: the IC sets the bit corresponding to the
pressed key and clears all others.

K7 and K8 both have bit 6 set alongside two lower bits. Bit 6 likely flags
the timer category; the lower bits then identify the specific duration.

The IC most likely maps each button directly to a fixed byte scanned from a
resistor ladder or key matrix, with K1–K6 as primary function keys and
K7–K8 as combined speed+timer keys.

---

## Timing summary

| Parameter               | Measured value               |
|-------------------------|------------------------------|
| Carrier frequency       | 38.03 kHz                    |
| Long mark / short space | ~1260 µs / ~420 µs (bit = 1) |
| Short mark / long space | ~420 µs / ~1260 µs (bit = 0) |
| Bit duration            | ~1683 µs (constant)          |
| Inter-frame gap         | ~6.2 ms (0xEC units)         |
| Final silence           | ~66 ms (0x09D8 units)        |
| Mini-frame length       | 12 symbols / 12 bits         |
| Preamble A payload      | `0x00` (`00000000`)          |
| Preamble B payload      | `0x7F` (`01111111`)          |
| Command repeats         | 3–6×                         |

---

## Conclusion

The remote uses a minimal proprietary pulse-distance protocol at 38 kHz with
no NEC or RC-5 framing. Each button press transmits three distinct mini-frames:
a fixed preamble pair followed by a repeating 8-bit command byte. The command
set appears to use active-low one-hot bit assignment across an 8-bit field.
Both brands respond identically to the same remote, suggesting the OEM IC is
the sole source of both products' RF identity.
