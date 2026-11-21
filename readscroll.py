#!/usr/bin/env python3
"""readscroll — headless hands-free scrolling for Fedora KDE Plasma (Wayland).

Thin launcher for the readscroll_lib package. All constants live in
readscroll_lib/config.py, the main loop in readscroll_lib/app.py.
"""

from __future__ import annotations

import sys

from readscroll_lib.app import main

if __name__ == "__main__":
    sys.exit(main())
