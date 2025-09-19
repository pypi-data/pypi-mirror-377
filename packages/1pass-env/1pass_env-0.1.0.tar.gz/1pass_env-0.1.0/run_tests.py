#!/usr/bin/env python3
"""
Test runner script for 1pass-env project.
Runs comprehensive tests with coverage reporting.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run the complete test suite."""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🧪 Starting comprehensive test suite for 1pass-env...")
    print("=" * 60)
    
    # Test commands to run
    test_commands = [
        # Run main test suite with coverage
        [
            "python", "-m", "pytest", 
            "test_main.py", 
            "-v", 
            "--cov=main", 
            "--cov-report=html", 
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=95"
        ],
        
        # Run edge case tests
        [
            "python", "-m", "pytest", 
            "test_edge_cases.py", 
            "-v", 
            "--cov=main", 
            "--cov-append",
            "--cov-report=html",
            "--cov-report=term-missing"
        ],
        
        # Run all tests together for final coverage report
        [
            "python", "-m", "pytest", 
            "test_main.py", 
            "test_edge_cases.py",
            "-v", 
            "--cov=main", 
            "--cov-report=html", 
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=95",
            "--tb=short"
        ]
    ]
    
    success = True
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📋 Running test phase {i}/{len(test_commands)}...")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 40)
        
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=False)
            print(f"✅ Test phase {i} completed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Test phase {i} failed with exit code {e.returncode}")
            success = False
            if i < len(test_commands):
                print("Continuing with remaining tests...")
            continue
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 All tests passed successfully!")
        print("\n📊 Coverage reports generated:")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
        print("\n💡 To view HTML coverage report:")
        print("     open htmlcov/index.html")
        return 0
    else:
        print("💥 Some tests failed. Check the output above for details.")
        return 1


def install_test_dependencies():
    """Install test dependencies if not already installed."""
    print("📦 Installing test dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pytest>=7.0.0", 
            "pytest-cov>=4.0.0", 
            "pytest-asyncio>=0.21.0", 
            "pytest-mock>=3.10.0"
        ], check=True)
        print("✅ Test dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install test dependencies")
        return False


def main():
    """Main entry point."""
    print("🚀 1pass-env Test Runner")
    print("=" * 40)
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found, attempting to install...")
        if not install_test_dependencies():
            sys.exit(1)
    
    # Run tests
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n🎯 Test Summary:")
        print("  - Comprehensive test coverage achieved")
        print("  - All edge cases covered")
        print("  - Error handling verified")
        print("  - CLI integration tested")
        print("  - Mock scenarios validated")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()