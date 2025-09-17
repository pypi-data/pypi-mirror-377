"""
Pytest configuration and fixtures for Dynex SDK tests
"""
import os
import tempfile
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch

import dynex
from dynex import DynexConfig


@pytest.fixture(scope="session")
def test_config():
    """Create a test configuration for all tests"""
    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp(prefix="dynex_test_")
    
    # Create a minimal test configuration
    config_content = f"""[DYNEX]
api_key = test_key
api_secret = test_secret
api_endpoint = https://test-api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = test-ftp.dynex.dev
ftp_username = test_user
ftp_password = test_pass
"""
    
    config_path = Path(temp_dir) / "dynex.ini"
    config_path.write_text(config_content)
    
    # Create solver directory
    solver_dir = Path(temp_dir) / "testnet"
    solver_dir.mkdir(exist_ok=True)
    
    # Create a mock solver executable
    mock_solver = solver_dir / "dynexcore"
    mock_solver.write_text("#!/bin/bash\necho 'Mock solver'")
    mock_solver.chmod(0o755)
    
    # Set environment variables for testing
    env_vars = {
        "DYNEX_API_KEY": "test_key",
        "DYNEX_API_SECRET": "test_secret", 
        "DYNEX_API_ENDPOINT": "https://test-api.dynex.dev",
        "DYNEX_FTP_HOSTNAME": "test-ftp.dynex.dev",
        "DYNEX_FTP_USERNAME": "test_user",
        "DYNEX_FTP_PASSWORD": "test_pass",
    }
    
    with patch.dict(os.environ, env_vars):
        config = DynexConfig(
            config_path=str(config_path),
            solver_path=str(solver_dir),
            mainnet=False,  # Use testnet for all tests
            is_logging=False,  # Disable logging for cleaner test output
            solver_version=2
        )
        yield config
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_api():
    """Mock DynexAPI for testing without network calls"""
    with patch('dynex.api.DynexAPI') as mock:
        mock_instance = Mock()
        mock_instance.account_status.return_value = {"status": "active", "balance": 1000}
        mock_instance.create_job_api.return_value = (12345, "test_file.dnx", 0.001, None)
        mock_instance.update_job_api.return_value = True
        mock_instance.finish_job_api.return_value = True
        mock_instance.cancel_job_api.return_value = True
        mock_instance.get_status_details_api.return_value = (0, 0.0, 0, "")
        mock_instance.report_invalid.return_value = True
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_bqm():
    """Create a sample BQM for testing"""
    import dimod
    return dimod.BinaryQuadraticModel(
        {'x1': 1.0, 'x2': -1.5, 'x3': 2.0},
        {('x1', 'x2'): 1.0, ('x2', 'x3'): -2.0},
        0.0, 
        dimod.BINARY
    )


@pytest.fixture
def sample_sat_clauses():
    """Create sample SAT clauses for testing"""
    return [
        [1, -2, 3], [-1, 4, 5], [6, 7, -8], 
        [-9, -10, 11], [12, 13, -14], [-1, 15, -16]
    ]


@pytest.fixture
def sample_cqm():
    """Create a sample CQM for testing"""
    import dimod
    
    num_widget_a = dimod.Integer('num_widget_a', upper_bound=7)
    num_widget_b = dimod.Integer('num_widget_b', upper_bound=3)
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.set_objective(-3 * num_widget_a - 4 * num_widget_b)
    cqm.add_constraint(num_widget_a + num_widget_b <= 5, label='total widgets')
    
    return cqm


@pytest.fixture
def sample_dqm():
    """Create a sample DQM for testing"""
    import dimod
    
    dqm = dimod.DiscreteQuadraticModel()
    dqm.add_variable(3, label='my_hand')
    dqm.add_variable(3, label='their_hand')
    
    return dqm


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests"""
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests
    yield
    # Cleanup after test
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp(prefix="dynex_test_")
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
