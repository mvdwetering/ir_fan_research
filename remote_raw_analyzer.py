#!/usr/bin/env python3

import argparse
import json
import logging
import re
import statistics

# [D][remote.raw:041]: Received Raw: 84
# [D][remote.raw:028]: Received Raw: 1252, -426, 1238, -442, 414, -1274, 442, -1245, 442, -1246, 442, -1247, 447, -1241, 441, -1246, 441, -1249, 416, -1270, 441, -1247, 415, -7443, 1303, -401, 1191, -491, 413, -1272, 443, -1244, 416, -1276, 1193, -495, 1190, -492, 1193, -493,
# [D][remote.raw:028]:   1192, -492, 1192, -494, 1191, -491, 1194, -6651, 1253, -424, 1192, -491, 444, -1242, 417, -1268, 416, -1274, 441, -1247, 418, -1268, 417, -1272, 418, -1270, 442, -1245, 443, -1249, 1192, -6652, 1286, -393, 1191, -493, 438, -1245, 445, -1241, 418,
# [D][remote.raw:028]:   -1271, 418, -1269, 443, -1245, 447, -1242, 443, -1243, 447, -1239, 445, -1246, 1241, -6606, 1286, -389, 1238, -444, 447, -1238, 474, -1216, 440, -1246, 446, -1242, 444, -1241, 477, -1212, 451, -1237, 447, -1240, 444, -1248, 1239, -6605, 1313, -392,
# [D][remote.raw:041]:   1235, -420, 442, -1242, 448, -1239, 476, -1209, 451, -1241, 447, -1239, 447, -1239, 447, -1243, 446, -1241, 447, -1240, 1268
regex = re.compile(r"remote.raw:(?P<number>\d\d\d)\]:(?P<receivedraw>.*?)\s+(?P<data>[-\d,\s]+)")

def decode_messages(inputfile):
    messages = []
    message = None
    with open(args.inputfile, "r") as logfile:
        for line in logfile:
            stripped_line = line.strip()
            m = regex.search(stripped_line)
            if m:
                # Starts a new message
                if m.group("receivedraw"):
                    if not m.group("data").split(',')[0].startswith('-'):
                        message = []

                # Handle data in message
                if message is not None:
                    data = m.group("data").split(',')
                    for element in data:
                        if element.strip() != "":
                            message.append(int(element))

                # 041 indicates last part of message
                if m.group("number") == "041":
                    # filter out noise
                    if message and len(message) > 10:
                        messages.append(message)
                    message = None

    return messages


def main(args):

    messages = decode_messages(args.inputfile)

    if not args.spacing:
        id = 0
        buckets = []
        for message in messages:
            id += 1
            logging.debug(f"#{id}: {len(message)} {message}")

            abs_message = [abs(ele) for ele in message]
            logging.debug(f">> mean: {statistics.mean(abs_message)}, median: {statistics.median_grouped(abs_message)}")

            for element in abs_message:
                handled = False
                for bucket in buckets:
                    mean = statistics.mean(bucket) # This probably makes it slow
                    min = mean - mean/4 # 25% deviation is what the ESPHome receiver allows, so lets try that
                    max = mean + mean/4
                    if element >= min and element <= max:
                        bucket.append(element)
                        handled = True
                        break
                if not handled:
                    buckets.append([element])


        print("")
        print("List of buckets, use them to figure out spacing parameters")
        print("There should be 3 with significant more entries than the others.")
        print("The others should have very low numbers (lets say < 10).")
        print("----------------------------------------------------------")
        mean_len_buckets = {}
        for bucket in buckets:
            mean = statistics.mean(bucket)
            mean_len_buckets[mean] = len(bucket)
            print(f"mean: {mean}, len: {len(bucket)}")
            logging.debug(bucket)
        print("----------------------------------------------------------")

        sorted_by_len = sorted(mean_len_buckets.items(), key=lambda kv: kv[1])
        logging.debug(sorted_by_len)
        top_three = sorted_by_len[-3:]
        logging.debug(top_three)
        sorted_by_mean = sorted(top_three, key=lambda kv: kv[0])
        logging.debug(sorted_by_mean)

        print(f"Auto suggested spacing:")
        print(f"--spacing {round(sorted_by_mean[0][0])},{round(sorted_by_mean[1][0])},{round(sorted_by_mean[2][0])}")
        exit(0)


    spacing = []
    for space in args.spacing.split(","):
        spacing.append(int(space))

    id = 0
    for message in messages:
        id += 1
        abs_message = [abs(ele) for ele in message]

        idx = 0
        message_str = ""
        abs_message = [abs(ele) for ele in message]
        while idx < len (message):
            if (spacing[0] - spacing[0]/4) <  abs_message[idx] < (spacing[0] + spacing[0]/4):
                message_str += "0"
            elif (spacing[1] - spacing[1]/4) <  abs_message[idx] < (spacing[1] + spacing[1]/4):
                message_str += "1"
            else:
                logging.warning("Out of range: %s" % message[idx])
                message_str += "-"

            if idx + 1 < len(message):
                if (spacing[2] - spacing[2]/4) <  abs_message[idx+1] < (spacing[2] + spacing[2]/4):
                    message_str += " "

            idx += 2
        print(message_str)


if __name__ == "__main__":

    ## Commandlineoptions
    parser = argparse.ArgumentParser(description="Analyze remote.raw output from ESPHome irreceiver")

    parser.add_argument(
        "inputfile", help="File with output to analyze"
    )
    parser.add_argument(
        "--spacing",
        help="Give duration of the 3 parts of the signal in ms <short>,<long>,<space>. This will attempt to filter out bogus data.",
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Define loglevel, default is INFO.",
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    main(args)
