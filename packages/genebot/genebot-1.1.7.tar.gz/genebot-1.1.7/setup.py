#!/usr/bin/env python3
"""
GeneBot - Advanced Multi-Market Trading Bot
Modern setup script that defers to pyproject.toml for configuration

This setup.py exists for compatibility with older tools and build systems.
All package configuration is now defined in pyproject.toml following PEP 621.
"""

from setuptools import setup

# Modern Python packaging uses pyproject.toml for configuration
# This setup.py exists for compatibility with older tools
if __name__ == "__main__":
    setup()