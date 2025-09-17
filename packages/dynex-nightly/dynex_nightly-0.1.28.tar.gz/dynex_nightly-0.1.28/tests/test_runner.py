#!/usr/bin/env python3
"""
Test runner for Dynex SDK
This script can be used to run tests manually or in CI/CD
"""
import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import dynex
sys.path.insert(0, str(Path(__file__).parent.parent))

import dynex
from dynex import DynexConfig


def setup_test_environment():
    """Setup test environment with required configuration"""
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
    test_dir = Path(__file__).parent
    tmp_dir = test_dir / "tmp"
    solver_dir = test_dir / "testnet"
    
    tmp_dir.mkdir(exist_ok=True)
    solver_dir.mkdir(exist_ok=True)
    
    # Create mock solver executable
    mock_solver = solver_dir / "dynexcore"
    if not mock_solver.exists():
        mock_solver.write_text("#!/bin/bash\necho 'Mock solver for testing'")
        mock_solver.chmod(0o755)
    
    return test_dir


def run_basic_tests():
    """Run basic functionality tests"""
    print("Running basic functionality tests...")
    
    try:
        # Test configuration
        config = DynexConfig(mainnet=False, is_logging=False)
        print("✓ Configuration test passed")
        
        # Test basic imports
        from dynex import BQM, SAT, CQM, DQM, DynexSampler, DynexAPI
        print("✓ Import tests passed")
        
        # Test utility functions
        dynex.test()
        print("✓ Utility test function passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic tests failed: {e}")
        return False


def run_pytest_tests(test_dir, args):
    """Run pytest tests"""
    print(f"Running pytest tests from {test_dir}...")
    
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "-v",
        "--tb=short"
    ]
    
    if args.coverage:
        pytest_cmd.extend(["--cov=dynex", "--cov-report=term-missing"])
    
    if args.html:
        pytest_cmd.extend(["--cov-report=html:htmlcov"])
    
    if args.xml:
        pytest_cmd.extend(["--cov-report=xml"])
    
    if args.markers:
        pytest_cmd.extend(["-m", args.markers])
    
    if args.verbose:
        pytest_cmd.append("-s")
    
    try:
        result = subprocess.run(pytest_cmd, cwd=test_dir.parent, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Pytest execution failed: {e}")
        return False


def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    
    try:
        # Test complete workflow
        import dimod
        from dynex import BQM, DynexSampler, DynexConfig
        
        # Create test BQM
        bqm = dimod.BinaryQuadraticModel(
            {'x1': 1.0, 'x2': -1.5, 'x3': 2.0},
            {('x1', 'x2'): 1.0, ('x2', 'x3'): -2.0},
            0.0, 
            dimod.BINARY
        )
        
        # Create model and sampler
        config = DynexConfig(mainnet=False, is_logging=False)
        model = BQM(bqm, config=config)
        sampler = DynexSampler(model, config=config)
        
        print("✓ Integration test setup passed")
        return True
        
    except Exception as e:
        print(f"✗ Integration tests failed: {e}")
        return False


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Dynex SDK Test Runner")
    parser.add_argument("--basic", action="store_true", help="Run basic functionality tests")
    parser.add_argument("--pytest", action="store_true", help="Run pytest tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--xml", action="store_true", help="Generate XML coverage report")
    parser.add_argument("--markers", type=str, help="Run tests with specific markers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup test environment
    test_dir = setup_test_environment()
    
    # Determine which tests to run
    if args.all or (not any([args.basic, args.pytest, args.integration])):
        args.basic = True
        args.pytest = True
        args.integration = True
    
    success = True
    
    # Run tests
    if args.basic:
        success &= run_basic_tests()
    
    if args.pytest:
        success &= run_pytest_tests(test_dir, args)
    
    if args.integration:
        success &= run_integration_tests()
    
    # Print results
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
