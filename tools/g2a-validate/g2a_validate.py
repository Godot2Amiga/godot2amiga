#!/usr/bin/env python3
"""Compatibility launcher for the packaged g2a validator."""

from g2a.validate import main

if __name__ == "__main__":
    raise SystemExit(main())
