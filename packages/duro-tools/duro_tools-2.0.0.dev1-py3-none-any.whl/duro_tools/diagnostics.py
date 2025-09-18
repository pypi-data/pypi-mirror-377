#!/usr/bin/env python
# Copyright (C) 2025 Carnegie Robotics LLC.
# Contact: CRL Support<support@carnegierobotics.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
from __future__ import absolute_import, print_function

import struct
import time

import yaml

from sbp.bootload import (SBP_MSG_BOOTLOADER_HANDSHAKE_DEP_A,
                          SBP_MSG_BOOTLOADER_HANDSHAKE_RESP,
                          MsgBootloaderJumpToApp, MsgBootloaderHandshakeResp)
from sbp.client import Framer, Handler
from sbp.logging import SBP_MSG_LOG, SBP_MSG_PRINT_DEP
from sbp.piksi import MsgReset
from sbp.settings import (
    SBP_MSG_SETTINGS_READ_BY_INDEX_DONE, SBP_MSG_SETTINGS_READ_BY_INDEX_REQ,
    SBP_MSG_SETTINGS_READ_BY_INDEX_RESP, MsgSettingsReadByIndexReq)
from sbp.system import SBP_MSG_HEARTBEAT, MsgHeartbeat

from . import serial_link
from duro_tools.settings import Settings

DIAGNOSTICS_FILENAME = "diagnostics.yaml"

class Diagnostics(object):
    """
    Diagnostics

    The :class:`Diagnostics` class collects devices diagnostics.
    """

    def __init__(self, link, timeout=None):
        self.diagnostics = {}
        self.diagnostics['versions'] = {}
        self.diagnostics['settings'] = {}
        self.settings_received = False
        self.heartbeat_received = False
        self.handshake_received = False
        self.sbp_version = (0, 0)
        self.link = link

        self.link.add_callback(self._heartbeat_callback, SBP_MSG_HEARTBEAT)

        timeout = time.time() + timeout if timeout is not None else None
        # Wait for the heartbeat
        while not self.heartbeat_received:
            time.sleep(0.1)
            if timeout is not None and time.time() > timeout:
                print("timeout waiting for heartbeat")

                return
        print("received heartbeat")

        # Wait for the settings
        with Settings(link) as settings:
            self.diagnostics['settings'] = dict(settings.read_all())
        print("received settings")

    def _print_callback(self, msg, **metadata):
        print(msg.text)

    def _heartbeat_callback(self, sbp_msg, **metadata):
        msg = MsgHeartbeat(sbp_msg)
        self.sbp_version = (msg.flags >> 16) & 0xFF, (msg.flags >> 8) & 0xFF
        self.diagnostics['versions']['sbp'] = '%d.%d' % self.sbp_version
        self.heartbeat_received = True

def parse_device_details_yaml(device_details):
    """Parse from yaml string the device settings.

    """
    return yaml.load(device_details)['settings']['system_info']


def check_diagnostics(diagnostics_filename, version):
    """Check that Piksi's firmware/nap settings are properly set.

    Given a diagnostics_filename output and an expected firmware/NAP
    versions (via a Yaml string), returns True if expected fw/nap are
    properly loaded.

    """
    if version is None:
        raise Exception("Empty version string!")
    parsed = yaml.load(version)
    fw = parsed.get('fw', None)
    nap = parsed.get('hdl', None)
    with open(diagnostics_filename, 'r+') as f:
        details = parse_device_details_yaml(f.read())
        firmware_version = details.get('firmware_version', None)
        nap_version = details.get('nap_version', None)
        return (firmware_version and nap_version) \
            and (firmware_version == fw and nap_version == nap)

def get_args():
    """
    Get and parse arguments.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Acquisition Monitor')
    parser = serial_link.base_cl_options()

    parser.add_argument(
        "-o",
        "--diagnostics-filename",
        default=[DIAGNOSTICS_FILENAME],
        nargs=1,
        help="file to write diagnostics to.")
    return parser.parse_args()

def main():
    """
    Get configuration, get driver, and build handler and start it.
    """
    args = get_args()
    driver = serial_link.get_base_args_driver(args)
    diagnostics_filename = args.diagnostics_filename[0]

    with Handler(Framer(driver.read, driver.write)) as link:
        diagnostics = Diagnostics(link).diagnostics
        with open(diagnostics_filename, 'w') as diagnostics_file:
            yaml.dump(
                diagnostics, diagnostics_file, default_flow_style=False)
            print("wrote diagnostics file")

if __name__ == "__main__":
    main()
