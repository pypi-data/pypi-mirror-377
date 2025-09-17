from __future__ import annotations

# from .physio_cassette import *
__all__ = [
    'XLSDictReader',
    'DataHolder',
    'SignalbyEvent',
    'Signal',
    'SignalFrame',
    'EventRecord',
    'EventFrame',
    'autocache'
]
from .physio_cassette import (
    DataHolder,
    EventFrame,
    EventRecord,
    Signal,
    SignalbyEvent,
    SignalFrame,
    XLSDictReader,
    autocache,
)

__version__ = "0.2.15"
__author__      = "Luca Cerina"
__copyright__   = "Copyright 2022-2025, Luca Cerina"
__email__       = "lccerina@duck.com"