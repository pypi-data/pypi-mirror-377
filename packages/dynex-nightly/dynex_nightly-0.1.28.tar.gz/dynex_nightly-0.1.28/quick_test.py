#!/usr/bin/env python3
"""
Quick test script for Dynex SDK
This script provides a simple way to test the library without complex setup
"""
import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_test_environment():
    """Setup minimal test environment"""
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
    
    # Create temporary directories
    temp_dir = tempfile.mkdtemp(prefix="dynex_test_")
    tmp_dir = Path(temp_dir) / "tmp"
    solver_dir = Path(temp_dir) / "testnet"
    
    tmp_dir.mkdir(exist_ok=True)
    solver_dir.mkdir(exist_ok=True)
    
    # Create mock solver
    mock_solver = solver_dir / "dynexcore"
    mock_solver.write_text("#!/bin/bash\necho 'Mock solver for testing'")
    mock_solver.chmod(0o755)
    
    # Create config file
    config_content = f"""[DYNEX]
api_key = test_key_12345
api_secret = test_secret_67890
api_endpoint = https://test-api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = test-ftp.dynex.dev
ftp_username = test_user
ftp_password = test_password
"""
    config_path = Path(temp_dir) / "dynex.ini"
    config_path.write_text(config_content)
    
    # Set config path environment variable
    os.environ['DYNEX_CONFIG'] = str(config_path)
    os.environ['DYNEX_SOLVER'] = str(solver_dir)
    
    return temp_dir, str(solver_dir)

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    try:
        import dynex
        from dynex import DynexConfig, DynexAPI, BQM, SAT, CQM, DQM, DynexSampler
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration creation"""
    print("Testing configuration...")
    try:
        from dynex import DynexConfig
        config = DynexConfig(mainnet=False, is_logging=False)
        print(f"✓ Configuration created: mainnet={config.mainnet}, solver_version={config.solver_version}")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False

def test_models():
    """Test model creation"""
    print("Testing model creation...")
    try:
        import dimod
        from dynex import BQM, SAT, CQM, DQM, DynexConfig
        
        config = DynexConfig(mainnet=False, is_logging=False)
        
        # Test BQM
        bqm = dimod.BinaryQuadraticModel({'x1': 1.0, 'x2': -1.5}, {('x1', 'x2'): 1.0}, 0.0, dimod.BINARY)
        model_bqm = BQM(bqm, config=config)
        print(f"✓ BQM model created: {model_bqm.type}")
        
        # Test SAT
        clauses = [[1, -2, 3], [-1, 4, 5]]
        model_sat = SAT(clauses, config=config)
        print(f"✓ SAT model created: {model_sat.type}")
        
        # Test CQM
        num_widget_a = dimod.Integer('num_widget_a', upper_bound=7)
        num_widget_b = dimod.Integer('num_widget_b', upper_bound=3)
        cqm = dimod.ConstrainedQuadraticModel()
        cqm.set_objective(-3 * num_widget_a - 4 * num_widget_b)
        cqm.add_constraint(num_widget_a + num_widget_b <= 5, label='total widgets')
        model_cqm = CQM(cqm, config=config)
        print(f"✓ CQM model created: {model_cqm.type}")
        
        # Test DQM
        dqm = dimod.DiscreteQuadraticModel()
        dqm.add_variable(3, label='my_hand')
        dqm.add_variable(3, label='their_hand')
        # Add some quadratic terms
        dqm.set_quadratic('my_hand', 'their_hand', {(0, 1): 1.0, (1, 0): -1.0})
        model_dqm = DQM(dqm, config=config)
        print(f"✓ DQM model created: {model_dqm.type}")
        
        return True
    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        return False

def test_sampler():
    """Test sampler creation"""
    print("Testing sampler creation...")
    try:
        import dimod
        from dynex import BQM, DynexSampler, DynexConfig
        
        config = DynexConfig(mainnet=False, is_logging=False)
        bqm = dimod.BinaryQuadraticModel({'x1': 1.0, 'x2': -1.5}, {('x1', 'x2'): 1.0}, 0.0, dimod.BINARY)
        model = BQM(bqm, config=config)
        sampler = DynexSampler(model, config=config)
        print(f"✓ Sampler created: {sampler.state}")
        return True
    except Exception as e:
        print(f"✗ Sampler creation failed: {e}")
        return False

def test_api():
    """Test API creation"""
    print("Testing API creation...")
    try:
        from dynex import DynexAPI, DynexConfig
        
        config = DynexConfig(mainnet=False, is_logging=False)
        api = DynexAPI(config=config)
        print(f"✓ API created: logging={api.logging}")
        return True
    except Exception as e:
        print(f"✗ API creation failed: {e}")
        return False

def test_utilities():
    """Test utility functions"""
    print("Testing utility functions...")
    try:
        import dynex
        from unittest.mock import patch
        
        # Mock the FTP connection to avoid network errors
        with patch('dynex.sampler.FTP') as mock_ftp:
            mock_ftp_instance = mock_ftp.return_value
            mock_ftp_instance.login.return_value = None
            mock_ftp_instance.cwd.return_value = None
            mock_ftp_instance.mlsd.return_value = []
            
            # Test utility function
            dynex.test()
            print("✓ Utility test function executed")
        return True
    except Exception as e:
        print(f"✗ Utility test failed: {e}")
        return False

def main():
    """Run all quick tests"""
    print("🚀 Running Dynex SDK Quick Tests")
    print("=" * 50)
    
    # Setup test environment
    temp_dir, solver_path = setup_test_environment()
    
    try:
        # Run tests
        tests = [
            test_imports,
            test_configuration,
            test_models,
            test_sampler,
            test_api,
            test_utilities,
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            if test_func():
                passed += 1
            print()
        
        # Results
        print("=" * 50)
        print(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Dynex SDK is working correctly.")
            return 0
        else:
            print("❌ Some tests failed. Check the output above for details.")
            return 1
            
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
