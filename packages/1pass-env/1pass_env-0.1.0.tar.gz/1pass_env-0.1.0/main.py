#!/usr/bin/env python3
"""
Simple entry point for 1pass-env CLI tool.

This file provides a backward-compatible entry point for users who might
be calling main.py directly. The main functionality has been moved to
the modular structure in src/onepass_env/.
"""

if __name__ == '__main__':
    try:
        from src.onepass_env.cli import main
        main()
    except ImportError:
        # Fallback for different installation contexts
        try:
            from onepass_env.cli import main
            main()
        except ImportError:
            print("Error: onepass_env package not found. Please install it first.")
            print("Run: pip install -e .")
            exit(1)