# 1603 - Update the docs for SilverCrest Fan compatibility (Misting Pedestal Fan / SilverCrest SSVS 85 A1 Fan)

link: <https://github.com/crankyoldgit/IRremoteESP8266/issues/1603>

## Description

This issue requests to update the documentation with details of a SilverCrest fan

This document extracts the most relevant parts.

## Supported products

Product: Misting Pedestal Fan / SilverCrest SSVS 85 A1 Fan
Brand: SilverCrest (Lidl)

Manual: <https://stesbintegrationprod.blob.core.windows.net/bsionlyarticlemanuals/bsiarticlemanual/360230/360230_PL.pdf>

## Button mapping

Note that these buttons are all toggles/cycles

| Button | Code  |    |
| ------ | ----- | -- |
| ON/OFF | 0x581 | K1 |
| Speed  | 0x582 | K2 |
| Mist   | 0x584 | K3 |
| Timer  | 0x588 | K4 |
| OSC    | 0x590 | K5 |

## Protocol insights

Note that this remote uses a different frame header and custom code than usual.

Frame header = 010
Custom code = 11
