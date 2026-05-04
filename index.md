# IR Fan research

## Background

This repo is to track my research on the IR protocol used by my IR ceiling fan with the end goal to control/automate the fan from Home Assistant.

I already tried this a few years back and fried the remote when trying to measure the signals (electrically) so the project went on hold for a bit. Back then I did get some IR captures with ESPHome on an esp01_1m ESP ESP8266 board, but I thought I could easier measure timing on the scope. These captures are added to the Emanuel directory.

I did manage to get a replacement/alternative remote by ordering a similar looking module/remote from Hornbach (Dutch DIY store). Fortunately that remote worked fine immediately, I did not even have to swap the module.

Anyway, Home Assistant 2026.4.0 added support for IR entities so I decided to give it another go. This time I got a [Seeed Studio XIAO IR Mate](https://www.seeedstudio.com/XIAO-Smart-IR-Mate-p-6492.html) IR transmitter/receiver that was mentioned in the 2026.4.0 release notes. Which is quite neat, but it needs a very slim USB-C plug (or a normal plug, a hobbyknife and some patience)

After flashing it with an ESPHome configuration that had an IR receiver component with logging it allowed capturing of the IR signals. Unfortunately these codes did not seem to be any sort of standard protocol. ESPHome thinks it is SYMPHONY protocol, but the data is `C00` for every button so that seems to be a false detection (spoiler: not really). Fortunately also the Pronto codes were displayed to allow for further analysis.

## The scripts

### legacy_remote_raw_analyzer.py

This script was used to figure out the "shape" of the data in my initial attempt a couple of years ago. I don't remember much of it.
It is mostly here for historic documentation

### decode_ir_messages.py

A script to decode raw IR data or pronto data file with the protocol knowledge we now have. It also generates some statistics.
This was entirely AI generated and iterated on quite a bit. I think the output seems fine, but be sceptical.

## The result (for now)

It turns out the protocol is what is called "Symphony" by IrRemoteESP8266 and ESPHome with a small twist. While the frame data is as described in the SM5012 datasheet, the message starts with a frame that has value 0x00 (all 0), then a frame with value 0x7F (all 1) and after that it sends frames with the actual button payload as long as the button is held down.

I named the initial frames "START_A" and "START_B" and will refer to messages starting with these frames as the "XIN HUI" variant by lack of a better names.

So the initial indication of Symphony protocol with data "C00" that the decoding from ESPHome is correct because the is what is in the first frame. But because every message start with such a frame it is not very useful.

### Typical message

This is the output from the `decode_ir_messages.py` script.

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

## Products

These are products I own or am confident are using the same IR protocol (XIN HUI variant).

* "Emanuel" - Ceiling fan Emanuel from lampen24.nl (2020)
* "Madeira" - IR fan controller from Hornbach to control Madeira ceiling fans

These products should ise the same protocol based on the data I found

* DD2 remote (no brand name, but might be good enough)
* Lindby (no model provided)

These products are bit less clear, but have a good chance of working

* Lindby, e.g. <https://www.lampen24.nl/p/plafondventilator-met-verlichting-auraya-stil-staal-10027100.html>
* Westinghouse, e.g. <https://www.lampen24.nl/p/westinghouse-bendan-ventilator-met-licht-zilver-9602244.html>

These products use the SM5012 variant ("standard" Symphony) based on data I found

* Symphony Air Cooler 3Di
* Brand: Blyss, Model: Owen-SW-5 3 speed Fan with water mist (has photos)
* Brand: Blyss, Model: WP-YK8 090218 Owen-SW-5 3 speed Fan with water mist remote
* Brand: Westinghouse, Model: Unknown Ceiling fan with lights
* Brand: Westinghouse, Model: 78095 Ceiling Fan Remote
* Brand: Satellite electronic, Model ID6 Ceiling Fan Remote
* Brand: SilverCrest (Lidl) Product: Misting Pedestal Fan / SilverCrest SSVS 85 A1 Fan
* Westinghouse with remote model ID6
* Brand: Vornado Product: Transom
