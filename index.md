# IR Fan research

## Background

This repo is to track my research on the IR protocol used by my IR ceiling fan with the end goal to control/automate the fan from Home Assistant.

I already tried this a few years back and fried the remote when trying to measure the signals (electrically) so the project went on hold for a bit. I did get some IR captures with ESPHome on an ESP ESP8266 board: esp01_1m, but I thought I could easier measure timing on the scope. These captures are added to the Emanuel directory.

I did manage to get a replacement/alternative remote by ordering a similar looking module/remote from Hornbach (Dutch DIY store). Fortunately that remote worked fine immediately, I did not even have to swap the module.

Anyway, Home Assistant 2026.4.0 added support for IR entities so I decided to give it another go. This time I got a [Seeed Studio XIAO IR Mate](https://www.seeedstudio.com/XIAO-Smart-IR-Mate-p-6492.html) IR transmitter/receiver that was mentioned in the 2026.4.0 release notes.

After flashing it with an ESPHome configuration that had an IR receiver component with logging it allowed capturing of the IR signals. Unfortunately these codes did not seem to be any sort of standard protocol. ESPHome thinks it is SYMPHONY protocol, but the data is always `C00` so that seems to be a false detection. Fortunately also the Pronto codes were displayed to allow for further analysis.

## The scripts

### legacy_remote_raw_analyzer.py

This script was used to figure out the "shape" of the data in my initial attempt a couple of years ago. I don't remember much of it.
It is mostly here for historic documentation

### decode_ir_messages.py

A script to decode raw IR data or pronto data with the protocol knowledge we now have. It also generates some statistics.
This was entirely AI generated, be sceptical about the output.

## Temp notes, needs processing

### Findings

* Both remotes have the same numbers on the PCB (AA2009-9/PC2C) and AA2009-9EIR is also mentioned as MODEL NO on the Madeira controller.
* The remotes send the same IR codes even though they have different model numbers AA2 vs AA3. The light on/off on AA3 turns on my light and the 2H on the AA3 turns off my light, so exactly like the buttons on that postionon the AA2 remote.
* The IC in the remote does not have any marking, see photos

So in the end just looking at the hardware did not really help in getting relevant info for the IR protocol. It also seems that noone has attempted to deocde the IR signals yet.
We do know that there are more remote models out that use the same protocol.

### Confirmed products

These are products I own or am confident are using the same IR protocol.

* "Emanuel" - Ceiling fan Emanuel from lampen24.nl
* "Madeira" - IR fan controller from Hornbach to control Madeira ceiling fans

### Potential products

Browsing lampen24.nl I suspect these are using the same module and with that the same IR protocol.
This is based on how the manual looks the same/similar as the one for my Emanual light.

* Lindy, e.g. <https://www.lampen24.nl/p/plafondventilator-met-verlichting-auraya-stil-staal-10027100.html>
* Westinghouse, e.g. <https://www.lampen24.nl/p/westinghouse-bendan-ventilator-met-licht-zilver-9602244.html>
