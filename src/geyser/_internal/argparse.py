import argparse
from argparse import ArgumentParser, Namespace
from importlib.metadata import metadata


def parser() -> ArgumentParser:
    p = ArgumentParser(
        prog='geyser',
    )
    p.add_argument(
        'args',
        nargs='*'
    )
    p.add_argument(
        '-V', '--version',
        action='version',
        version=metadata("geyser")['Version']
    )
    p.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='enable verbose mode'
    )
    return p
