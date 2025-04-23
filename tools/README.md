# SwipeVerse Development Tools

This directory contains utility scripts and tools for SwipeVerse development and testing.

## Build Tool

- `build.py` - Build script for packaging SwipeVerse for different platforms
  - Usage: `python tools/build.py dist` - Build Python distribution packages
  - Usage: `python tools/build.py platform --platform desktop` - Build for desktop platform

## Flet Test Scripts

These scripts are used to test and debug Flet framework functionality:

- `test_flet.py` - Displays Flet version and available attributes
- `test_flet_module.py` - Checks Flet installation and provides detailed module information
- `test_flet_path.py` - Shows the installed location of the Flet package
- `test_props.py` - Tests Flet component properties
- `test_scroll.py` - Lists scroll-related attributes in Flet Row component

These test scripts are useful for debugging Flet-related issues during development.