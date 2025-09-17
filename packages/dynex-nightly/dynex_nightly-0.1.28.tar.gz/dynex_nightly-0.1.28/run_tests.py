#!/usr/bin/env python3
"""
Comprehensive test runner for Dynex SDK
This script provides an easy way to run all tests with proper configuration
"""
import os
import sys
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path

def setup_environment():
    """Setup test environment"""
    # Set test environment variables
    test_env = {
        'DYNEX_API_KEY': 'test_key_12345',
        'DYNEX_API_SECRET': 'test_secret_67890',
        'DYNEX_API_ENDPOINT': 'https://test-api.dynex.dev',
        'DYNEX_FTP_HOSTNAME': 'test-ftp.dynex.dev',
        'DYNEX_FTP_USERNAME': 'test_user',
        'DYNEX_FTP_PASSWORD': 'test_password',
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    # Create test directories
    test_dir = Path(__file__).parent / "tests"
    tmp_dir = test_dir / "tmp"
    solver_dir = test_dir / "testnet"
    
    tmp_dir.mkdir(exist_ok=True)
    solver_dir.mkdir(exist_ok=True)
    
    # Create mock solver
    mock_solver = solver_dir / "dynexcore"
    if not mock_solver.exists():
        mock_solver.write_text("#!/bin/bash\necho 'Mock solver for testing'")
        mock_solver.chmod(0o755)
    
    return test_dir

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def run_quick_test():
    """Run quick functionality test"""
    print("🚀 Running quick functionality test...")
    return run_command([sys.executable, "quick_test.py"])

def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running unit tests...")
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-m", "not integration"]
    return run_command(cmd)

def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running integration tests...")
    cmd = [sys.executable, "-m", "pytest", "tests/test_integration.py", "-v", "-m", "integration"]
    return run_command(cmd)

def run_all_tests():
    """Run all tests"""
    print("🎯 Running all tests...")
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    return run_command(cmd)

def run_tests_with_coverage():
    """Run tests with coverage"""
    print("📊 Running tests with coverage...")
    cmd = [
        sys.executable, "-m", "pytest", "tests/", "-v",
        "--cov=dynex", "--cov-report=term-missing", "--cov-report=html"
    ]
    return run_command(cmd)

def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    cmd = [sys.executable, "-m", "flake8", "dynex", "tests", "--count", "--max-line-length=127"]
    return run_command(cmd)

def run_format_check():
    """Check code formatting"""
    print("🎨 Checking code formatting...")
    cmd = [sys.executable, "-m", "black", "--check", "dynex", "tests"]
    return run_command(cmd)

def run_import_check():
    """Check import sorting"""
    print("📦 Checking import sorting...")
    cmd = [sys.executable, "-m", "isort", "--check-only", "dynex", "tests"]
    return run_command(cmd)

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Dynex SDK Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick functionality test")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--lint", action="store_true", help="Run linting")
    parser.add_argument("--format", action="store_true", help="Check code formatting")
    parser.add_argument("--imports", action="store_true", help="Check import sorting")
    parser.add_argument("--ci", action="store_true", help="Run CI checks (all except coverage)")
    parser.add_argument("--full", action="store_true", help="Run full test suite with all checks")
    
    args = parser.parse_args()
    
    # Setup environment
    test_dir = setup_environment()
    
    # Determine what to run
    if args.full:
        args.quick = True
        args.unit = True
        args.integration = True
        args.coverage = True
        args.lint = True
        args.format = True
        args.imports = True
    elif args.ci:
        args.unit = True
        args.integration = True
        args.lint = True
        args.format = True
        args.imports = True
    elif not any([args.quick, args.unit, args.integration, args.all, args.coverage, args.lint, args.format, args.imports]):
        # Default: run all tests
        args.all = True
    
    # Track results
    results = []
    
    # Run selected tests
    if args.quick:
        results.append(("Quick Test", run_quick_test()))
    
    if args.unit:
        results.append(("Unit Tests", run_unit_tests()))
    
    if args.integration:
        results.append(("Integration Tests", run_integration_tests()))
    
    if args.all:
        results.append(("All Tests", run_all_tests()))
    
    if args.coverage:
        results.append(("Coverage Tests", run_tests_with_coverage()))
    
    if args.lint:
        results.append(("Linting", run_linting()))
    
    if args.format:
        results.append(("Format Check", run_format_check()))
    
    if args.imports:
        results.append(("Import Check", run_import_check()))
    
    # Print results
    print("\n" + "="*60)
    print("📋 TEST RESULTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print("="*60)
    print(f"Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All tests passed! Dynex SDK is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
