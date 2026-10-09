# Stuck with IR protocol (Westinghouse)

thread link: <https://community.home-assistant.io/t/stuck-with-ir-protocol/450180/5>
most relevant comment: <https://community.home-assistant.io/t/stuck-with-ir-protocol/450180/10>

## Description

The ESPHome thread has a person trying to figure out the IR codes for a Westinghouse ceiling fan.
It mentions the remote is a model "ID6"

This document extracts the most relevant parts.

## Supported products

Brand: Westinghouse

Remote model: ID6

## Button mapping

| Button           | Code  |    |
| ---------------- | ----- | -- |
| Light On         | 0xD88 | K4 |
| Light Off        | 0xDA0 | K6 |
| Fan Speed 0 (off)| 0xD90 | K5 |
| Fan Speed 1      | 0xD81 | K1 |
| Fan Speed 2      | 0xD82 | K3 |
| Fan Speed 3      | 0xDC3 | K7 |

## Protocol insights

Note that this remote does not use the standard custom code 00.

Custom code = 11

## ESP Home configuration

The configuraton contains the raw codes. These have also been extracted into individual files for easier analysis.

```yaml
remote_transmitter:
  pin: D6
  id: remote_transmitter_id
  carrier_duty_percent: 50%

switch:
  - platform: template
    name: "Master Bedroom Main Light"
    id: bedroom_light
    icon: "mdi:ceiling-light"
    optimistic: true
    turn_on_action:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [1378, -334, 1352, -334, 539, -1153, 1345, -336, 1351, -309, 561, -1151, 536, -1126, 533, -1178, 1350, -335, 536, -1151, 538, -1148, 509, -7922, 1350, -335, 1350, -312, 559, -1152, 1350, -335, 1351, -339, 532, -1153, 507, -1152, 559, -1127, 1375, -308, 563, -1151, 536, -1126, 533, -7922, 1376, -260, 1375, -360, 535, -1126, 1376, -335, 1351, -310, 561, -1152, 508, -1177, 509, -1154, 1374, -335, 537, -1149, 535, -1152, 508, -7899, 1348, -337, 1375, -334, 535, -1152, 1351, -334, 1352, -334, 536, -1152, 508, -1153, 559, -1128, 1374, -335, 535, -1152, 508, -1153, 533, -7923, 1350, -334, 1327, -359, 536, -1152, 1350, -334, 1352, -335, 535, -1127, 533, -1153, 558, -1153, 1350, -335, 537, -1150, 534, -1152, 534, -7872, 1375, -335, 1349, -337, 534, -1153, 1350, -335, 1351, -335, 535, -1152, 534, -1152, 509, -1177, 1351, -334, 536, -1152, 533, -1126, 561]
    turn_off_action:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [1405, -299, 1387, -301, 541, -1152, 1378, -299, 1387, -299, 516, -1179, 1379, -298, 542, -1129, 557, -1129, 559, -1130, 530, -1178, 535, -7895, 1378, -299, 1388, -297, 517, -1156, 1402, -299, 1386, -299, 519, -1177, 1378, -298, 517, -1179, 508, -1178, 534, -1127, 558, -1129, 558, -7897, 1350, -338, 1374, -301, 541, -1154, 1377, -299, 1387, -299, 542, -1154, 1378, -300, 515, -1179, 508, -1178, 534, -1126, 559, -1153, 534, -7871, 1402, -301, 1387, -298, 516, -1180, 1377, -301, 1386, -298, 517, -1179, 1378, -299, 516, -1179, 507, -1179, 534, -1152, 508, -1155, 557]


fan:
  - platform: template
    name: "Master Bedroom Fan"
    id: bedroom_fan
    speed_count: 3
    
    # Logic for when the Power button is pressed
    on_turn_on:
      then:
        - lambda: |-
            if (id(bedroom_fan).speed == 2) {
              id(ir_code_speed_2).execute();
            } else if (id(bedroom_fan).speed == 3) {
              id(ir_code_speed_3).execute();
            } else {
              id(ir_code_power_on_speed1).execute();
            }

    # Logic for when the Fan is turned off
    on_turn_off:
      then:
        - lambda: |-
            auto call = id(bedroom_fan).make_call();
            call.set_state(false);
            call.set_speed(1); // Force reset to Speed 1
            call.perform();
        - script.execute: ir_code_fan_off

    # Logic for when the slider/speed is changed
    on_speed_set:
      then:
        - if:
            condition:
              # Only send IR if the fan is already ON. 
              # If it's OFF, on_turn_on handles the IR to prevent double-firing.
              lambda: 'return id(bedroom_fan).state;'
            then:
              - if:
                  condition:
                    lambda: 'return x == 1;'
                  then:
                    - script.execute: ir_code_power_on_speed1
              - if:
                  condition:
                    lambda: 'return x == 2;'
                  then:
                    - script.execute: ir_code_speed_2
              - if:
                  condition:
                    lambda: 'return x == 3;'
                  then:
                    - script.execute: ir_code_speed_3
script:
  - id: ir_code_power_on_speed1
    then:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [1408, -296, 1387, -299, 543, -1153, 1379, -302, 1382, -300, 516, -1179, 535, -1151, 534, -1152, 509, -1178, 534, -1152, 509, -1178, 1381, -7026, 1374, -335, 1378, -299, 516, -1154, 1403, -298, 1387, -300, 542, -1127, 535, -1153, 559, -1128, 532, -1178, 508, -1177, 509, -1178, 1377, -7053, 1377, -300, 1387, -298, 517, -1179, 1382, -295, 1387, -301, 541, -1152, 509, -1177, 535, -1128, 532, -1178, 508, -1153, 537, -1174, 1377, -7029, 1401, -300, 1387, -299, 516, -1179, 1351, -334, 1379, -299, 516, -1179, 509, -1154, 532, -1177, 509, -1178, 508, -1177, 509, -1178, 1377, -7054, 1349, -335, 1352, -334, 535, -1152, 1351, -334, 1352, -334, 535, -1152, 534, -1128, 559, -1151, 509, -1177, 509, -1178, 508, -1178, 1350, -7081, 1325, -359, 1352, -336, 533, -1153, 1350, -334, 1351, -335, 537, -1127, 559, -1151, 534, -1152, 508, -1178, 509, -1177, 508, -1178, 1351]

  - id: ir_code_speed_2
    then:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [1377, -334, 1352, -335, 536, -1123, 1378, -335, 1351, -336, 539, -1123, 532, -1182, 504, -1178, 509, -1152, 1376, -307, 563, -1152, 534, -7896, 1325, -363, 1348, -335, 535, -1152, 1350, -336, 1350, -335, 535, -1152, 509, -1178, 533, -1152, 509, -1178, 1349, -335, 535, -1153, 508, -7896, 1327, -358, 1351, -335, 535, -1127, 1375, -335, 1352, -334, 536, -1151, 509, -1151, 535, -1156, 530, -1153, 1375, -334, 536, -1152, 534, -7872, 1374, -335, 1352, -334, 536, -1124, 1377, -335, 1352, -334, 536, -1152, 508, -1178, 534, -1151, 509, -1178, 1350, -335, 535, -1152, 508]

  - id: ir_code_speed_3
    then:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [1379, -309, 1377, -334, 535, -1152, 1350, -335, 1351, -309, 1377, -306, 564, -1152, 534, -1128, 533, -1152, 534, -1153, 1374, -307, 1380, -7057, 1373, -335, 1351, -336, 534, -1127, 1352, -359, 1351, -335, 1328, -358, 534, -1127, 533, -1179, 508, -1152, 537, -1177, 1323, -360, 1351, -7056, 1349, -361, 1350, -336, 534, -1153, 1328, -358, 1350, -335, 1350, -310, 561, -1151, 509, -1178, 508, -1178, 508, -1178, 1325, -360, 1352, -7080, 1324, -362, 1349, -336, 534, -1128, 1375, -335, 1326, -360, 1351, -335, 535, -1155, 531, -1151, 535, -1153, 508, -1153, 1374, -335, 1330]

  - id: ir_code_fan_off
    then:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [1404, -299, 1388, -299, 543, -1152, 1378, -299, 1387, -261, 581, -1127, 534, -1181, 1374, -299, 517, -1155, 532, -1153, 561, -1150, 509, -7896, 1403, -299, 1387, -299, 516, -1180, 1377, -299, 1387, -299, 517, -1179, 508, -1154, 1401, -299, 543, -1128, 561, -1126, 559, -1127, 558, -7897, 1350, -333, 1380, -300, 543, -1126, 1403, -300, 1386, -300, 516, -1154, 560, -1153, 1375, -300, 517, -1178, 509, -1158, 528, -1177, 508, -7899, 1374, -307, 1408, -297, 543, -1153, 1377, -303, 1383, -300, 542, -1128, 533, -1178, 1377, -300, 543, -1130, 557, -1127, 559, -1152, 508, -7897, 1403, -301, 1384, -299, 517, -1179, 1377, -299, 1387, -300, 543, -1152, 509, -1152, 1403, -299, 516, -1155, 586, -1128, 504, -1178, 509, -7896, 1407, -296, 1360, -334, 509, -1154, 1401, -300, 1386, -300, 543, -1153, 533, -1130, 1400, -256, 560, -1178, 535, -1152, 534, -1151, 509]
```
