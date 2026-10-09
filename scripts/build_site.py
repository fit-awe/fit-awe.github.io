#!/usr/bin/env python3
"""Regenerate every static page, including all shared homepage summaries."""
from build_publications import build
from build_personal_profile import build as build_personal_profile

if __name__ == '__main__':
    build()
    build_personal_profile()
