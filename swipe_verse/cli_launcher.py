#!/usr/bin/env python3
"""
Simple CLI launcher for Swipe Verse
"""
import sys

from swipe_verse.__main__ import main as _main


def main():
    """CLI entry point for Swipe Verse"""
    return _main()

if __name__ == "__main__":
    sys.exit(main())