# 1057 - Symphony fan remote without Bit mark

link: <https://github.com/crankyoldgit/IRremoteESP8266/issues/1057>

## Description

This issue requests to add support for a Symphony branded fan (which seems to be the reason the protocol is called Symphony)
It seems similar to the protocol my IR ceilingfan uses, just without the preambles.

Note that the implementation at this point assumed it was 11 bits which was fixed later, so only the capture and productname are relevant.

This document extracts the most relevant parts.

## Supported products

Manufacturer: Symphony
Model : Air Cooler 3Di

## Button mapping

Unknown

## IR captures

```text
button 1
1296,412,1294,386,420,1224,1322,390,1290,390,420,1224,452,1220,1314,394,420,1222,482,1190,480,1192,452,7960,1290,420,1290,390,418,1226,1318,394,1262,416,420,1224,454,1220,1292,416,422,1222,450,1222,452,1218,454,8208,1296,414,1292,386,418,1226,1292,422,1260,420,424,1218,454,1226,1312,390,420,1224,454,1220,482,1186,454,7960,1318,392,1264,416,392,1252,1318,394,1288,394,418,1224,452,1224,1292,422,414,1222,458,1214,450,1222,454

Button 2:
1324,386,1300,380,420,1224,1318,394,1266,414,418,1226,456,1216,448,1224,450,1224,454,1220,1296,410,422,7968,1310,392,1294,386,422,1224,1292,426,1282,390,420,1222,450,1224,452,1220,452,1220,448,1224,1322,388,420,8310,1322,386,1268,414,418,1224,1296,418,1288,390,418,1226,452,1220,454,1218,454,1220,480,1192,1322,388,420,7962,1318,390,1262,418,420,1224,1292,422,1294,386,424,1220,448,1222,452,1222,450,1222,452,1220,1290,418,420
```
