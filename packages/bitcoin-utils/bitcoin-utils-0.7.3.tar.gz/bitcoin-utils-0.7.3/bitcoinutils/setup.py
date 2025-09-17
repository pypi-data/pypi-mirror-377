# Copyright (C) 2018-2025 The python-bitcoin-utils developers
#
# This file is part of python-bitcoin-utils
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoin-utils, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

NETWORK = "testnet"

networks = {"mainnet", "testnet", "testnet4", "signet", "regtest"}


def setup(network: str = "testnet") -> str:
    global NETWORK
    NETWORK = network
    return NETWORK


def get_network() -> str:
    global NETWORK
    return NETWORK


def is_mainnet() -> bool:
    global NETWORK
    if NETWORK == "mainnet":
        return True
    else:
        return False


def is_testnet() -> bool:
    global NETWORK
    if NETWORK == "testnet":
        return True
    else:
        return False


def is_testnet4() -> bool:
    global NETWORK
    if NETWORK == "testnet4":
        return True
    else:
        return False


def is_signet() -> bool:
    global NETWORK
    if NETWORK == "signet":
        return True
    else:
        return False


def is_regtest() -> bool:
    global NETWORK
    if NETWORK == "regtest":
        return True
    else:
        return False
