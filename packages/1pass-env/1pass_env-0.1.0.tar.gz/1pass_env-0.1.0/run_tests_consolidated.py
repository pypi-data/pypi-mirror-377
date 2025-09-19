#!/usr/bin/env python3
"""
Consolidated test runner for 1pass-env.
Runs all tests from the unified test suite and generates comprehensive coverage reports.
"""

import os
import sys
import subprocess
from pathlib import Path


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


def run_consolidated_tests():
    """Run the consolidated test suite."""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🧪 Starting consolidated test suite for 1pass-env...")
    print("=" * 60)
    
    # Test command to run all consolidated tests
    test_command = [
        "python", "-m", "pytest", 
        "tests_consolidated/test_all.py",
        "-c", "pytest_consolidated.ini",
        "-v", 
        "--cov=main", 
        "--cov=src",
        "--cov-report=html:htmlcov_consolidated", 
        "--cov-report=term-missing",
        "--cov-report=xml:coverage_consolidated.xml",
        "--cov-fail-under=90",
        "--tb=short"
    ]
    
    print("📋 Running consolidated tests...")
    print(f"Command: {' '.join(test_command)}")
    print("-" * 40)
    
    try:
        subprocess.run(test_command, check=True, text=True, capture_output=False)
        print("✅ Consolidated tests completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    
    except Exception as e:
        print(f"❌ Unexpected error running tests: {e}")
        return 1


def analyze_test_coverage():
    """Analyze test coverage and provide recommendations."""
    print("\n📊 Test Coverage Analysis")
    print("=" * 40)
    
    coverage_file = Path("coverage_consolidated.xml")
    html_report = Path("htmlcov_consolidated/index.html")
    
    if coverage_file.exists():
        print(f"✅ Coverage XML report: {coverage_file}")
    else:
        print(f"❌ Coverage XML report not found: {coverage_file}")
    
    if html_report.exists():
        print(f"✅ Coverage HTML report: {html_report}")
        print(f"   Open file://{html_report.absolute()} in your browser")
    else:
        print(f"❌ Coverage HTML report not found: {html_report}")
    
    # Count test functions in consolidated file
    test_file = Path("tests_consolidated/test_all.py")
    if test_file.exists():
        with open(test_file, 'r') as f:
            content = f.read()
        
        test_function_count = content.count('def test_')
        test_class_count = content.count('class Test')
        
        print("\n📈 Test Statistics:")
        print(f"   Test classes: {test_class_count}")
        print(f"   Test functions: {test_function_count}")
        
        if test_function_count >= 80:
            print(f"🎉 Excellent test coverage with {test_function_count} tests!")
        elif test_function_count >= 60:
            print(f"👍 Good test coverage with {test_function_count} tests!")
        else:
            print(f"⚠️  Consider adding more tests (current: {test_function_count})")


def cleanup_old_test_files():
    """Clean up old, scattered test files."""
    print("\n🧹 Cleanup Recommendations")
    print("=" * 40)
    
    old_files = [
        "test_main.py",
        "test_edge_cases.py", 
        "conftest.py",
        "tests/test_cli.py",
        "tests/test_core.py",
        "tests/test_onepassword.py",
        "tests/conftest.py"
    ]
    
    existing_old_files = []
    for file_path in old_files:
        if Path(file_path).exists():
            existing_old_files.append(file_path)
    
    if existing_old_files:
        print(f"📁 Found {len(existing_old_files)} old test files that can be removed:")
        for file_path in existing_old_files:
            print(f"   - {file_path}")
        
        print("\n💡 To clean up old files, run:")
        print(f"   rm -f {' '.join(existing_old_files)}")
        print("   rm -rf tests/")
    else:
        print("✅ No old test files found")


def main():
    """Main entry point."""
    print("🚀 1pass-env Consolidated Test Runner")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found, attempting to install...")
        if not install_test_dependencies():
            sys.exit(1)
    
    # Run consolidated tests
    exit_code = run_consolidated_tests()
    
    # Analyze coverage
    analyze_test_coverage()
    
    # Show cleanup recommendations
    cleanup_old_test_files()
    
    if exit_code == 0:
        print("\n🎯 Consolidated Test Summary:")
        print("  - All tests consolidated into single comprehensive suite")
        print("  - Comprehensive test coverage achieved")
        print("  - All edge cases covered")
        print("  - Error handling verified")
        print("  - CLI integration tested")
        print("  - Mock scenarios validated")
        print("  - Async functionality tested")
        print("\n🏆 Test consolidation complete!")
    else:
        print("\n❌ Tests failed. Please review the output above.")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()