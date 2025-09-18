#!/usr/bin/env python3
"""This example demonstrates waiting for a published message to be fully acknowledged by the broker
before proceeding to send the next message.

It also demonstrates the debug logging output of the client.
"""

import argparse
import logging

from ohmqtt import Client, MQTTQoS


def main(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.DEBUG)
    with Client() as client:

        client.connect(args.address)
        client.wait_for_connect(timeout=5.0)

        for n in range(1, 9):
            client.publish(
                "ohmqtt/examples/publish_wait_for_ack", b"test_payload: " + str(n).encode(), qos=MQTTQoS.Q2
            ).wait_for_ack(timeout=5.0)

        client.disconnect()
        client.wait_for_disconnect(timeout=5.0)


if __name__ == "__main__":
    from .args import parser
    args = parser.parse_args()
    main(args)
