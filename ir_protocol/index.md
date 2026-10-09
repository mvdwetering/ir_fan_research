# IR protocol

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

The SM5021 datasheet describes each frame as a 12-bit transmitted word followed
by a four-bit empty synchronization field:

```text
[ Frame head: 110 ] [ Custom code: C1 C2 ] [ Control word: 7 bits ] [ Sync: 4 empty bits ]
```

For the captures documented here, the custom code is `00`. Thus each timed
mini-frame contains **12 mark/space pairs**: the three-bit head, two custom
bits, and seven-bit control word. The four empty sync bits appear as the
inter-frame silence rather than as additional mark/space data pairs.

The captures contain initial frames with control words `0000000` and `1111111`,
followed by the button's command frame repeated three to six times depending
on the button. These initial frames are observed in these captures; the SM5021
notes report that its variant starts directly with command frames.

### Field layout within each mini-frame

```text
[ 1 1 0 ] [ C1 C2 ] [ c6 c5 c4 c3 c2 c1 c0 ] [ four empty sync bits ]
  head      custom       seven-bit control word       synchronization
```

The observed head is `110` and custom code is `00`. The control word varies by
button and is listed in the command table below.

The head `110` is listed as "metal option", so it can be different.

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

| PCB label | Button | Frame word (12-bit) | Head | Custom code | Control word (7-bit) |
|-----------|--------|---------------------|------|-------------|----------------------|
| K1        | HI     | `110000000001`      | `110`| `00`        | `0000001`            |
| K2        | 8H     | `110000000010`      | `110`| `00`        | `0000010`            |
| K3        | MED    | `110000000100`      | `110`| `00`        | `0000100`            |
| K4        | ON/OFF | `110000001000`      | `110`| `00`        | `0001000`            |
| K5        | OFF    | `110000010000`      | `110`| `00`        | `0010000`            |
| K6        | 2H     | `110000100000`      | `110`| `00`        | `0100000`            |
| K7        | LOW    | `110001000011`      | `110`| `00`        | `1000011`            |
| K8        | 4H     | `110001000110`      | `110`| `00`        | `1000110`            |

### Pattern observation

Ordered by PCB label, the control words have the following bits set, in
ascending position:

| PCB label | Button | Control word | Set bit (0 = LSB) |
|-----------|--------|--------------|-------------------|
| K1        | HI     | `0000001`    | bit 0             |
| K2        | 8H     | `0000010`    | bit 1             |
| K3        | MED    | `0000100`    | bit 2             |
| K4        | ON/OFF | `0001000`    | bit 3             |
| K5        | OFF    | `0010000`    | bit 4             |
| K6        | 2H     | `0100000`    | bit 5             |
| K7        | LOW    | `1000011`    | bits 0, 1, and 6  |
| K8        | 4H     | `1000110`    | bits 1, 2, and 6  |

---

## Timing summary

| Parameter               | Measured value                     |
|-------------------------|------------------------------------|
| Carrier frequency       | 38.03 kHz                          |
| Long mark / short space | ~1260 µs / ~420 µs (bit = 1)       |
| Short mark / long space | ~420 µs / ~1260 µs (bit = 0)       |
| Bit duration            | ~1683 µs (constant)                |
| Inter-frame gap         | ~6.2 ms (0xEC units)               |
| Final silence           | ~66 ms (0x09D8 units)              |
| Transmitted frame word  | 12 symbols / 12 bits               |
| Frame head              | `110`                              |
| Custom code             | `00`                               |
| Control word            | 7 bits; varies by button           |
| Sync field              | 4 empty bits (inter-frame gap)     |
| Initial capture frames  | Control words `0000000`, `1111111` |
| Command repeats         | 3+                                 |

---

## Conclusion

The remote uses a proprietary pulse-width protocol at 38 kHz with no NEC, RC-5,
or RC-6 framing. The observed timed frame consists of the SM5021-style `110`
head, two-bit custom code, and seven-bit control word; the four-bit empty sync
field is represented by the inter-frame silence. These captures include two
initial control frames before repeated button commands, while the documented
SM5021 variant starts directly with the command frames. Both brands respond
identically to the same remote, suggesting shared or compatible OEM protocol
implementation.
