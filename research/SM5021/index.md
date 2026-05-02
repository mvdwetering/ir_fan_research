# SM5021

## Description

The SM5021 IR chip implements an encoder for a protocol which is _very_ similar as my ceiling fan uses.

Link to the datasheet of the [SM5021 IR chip](https://pdf1.alldatasheet.com/datasheet-pdf/view/124369/ANALOGICTECH/SM5021B.html)

The bit format is exactly the same. It also has the 110 prefix (metal option) then 2 bits custom code (00 for me)) and then payload options K1-K8 with same values as I have seen.

Main difference is that a message does not start with  the fixed frames with payload 0x00 and 0x7F. It immediately starts with the command frames. Also timing seems slightly different. I wonder if it is just hardware/crystal differences within allowed tolerances.
