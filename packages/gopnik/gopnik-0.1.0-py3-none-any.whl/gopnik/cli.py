#!/usr/bin/env python3
"""
Command-line entry point for Gopnik deidentification system.
"""

import sys
from .interfaces.cli import main

if __name__ == '__main__':
    sys.exit(main())