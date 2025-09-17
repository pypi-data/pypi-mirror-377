"""
Tests for DynexConfig class
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from dynex import DynexConfig


class TestDynexConfig:
    """Test cases for DynexConfig"""
    
    def test_config_creation_with_defaults(self, temp_dir):
        """Test creating config with default values"""
        # Create config file
        config_content = """[DYNEX]
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
        
        with patch.dict(os.environ, {
            'DYNEX_API_KEY': 'test_key',
            'DYNEX_API_SECRET': 'test_secret',
            'DYNEX_API_ENDPOINT': 'https://test-api.dynex.dev',
            'DYNEX_FTP_HOSTNAME': 'test-ftp.dynex.dev',
            'DYNEX_FTP_USERNAME': 'test_user',
            'DYNEX_FTP_PASSWORD': 'test_pass',
        }):
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir)
            )
            
            assert config.api_key == 'test_key'
            assert config.api_secret == 'test_secret'
            assert config.api_endpoint == 'https://test-api.dynex.dev'
            assert config.ftp_hostname == 'test-ftp.dynex.dev'
            assert config.ftp_username == 'test_user'
            assert config.ftp_password == 'test_pass'
            assert config.solver_version == 2
            assert config.mainnet is True
            assert config.is_logging is True
    
    def test_config_creation_with_parameters(self, temp_dir):
        """Test creating config with explicit parameters"""
        # Create config file
        config_content = """[DYNEX]
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
        
        with patch.dict(os.environ, {
            'DYNEX_API_KEY': 'test_key',
            'DYNEX_API_SECRET': 'test_secret',
            'DYNEX_API_ENDPOINT': 'https://test-api.dynex.dev',
            'DYNEX_FTP_HOSTNAME': 'test-ftp.dynex.dev',
            'DYNEX_FTP_USERNAME': 'test_user',
            'DYNEX_FTP_PASSWORD': 'test_pass',
        }):
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir),
                solver_version=1,
                mainnet=False,
                is_logging=False,
                retry_count=3
            )
            
            assert config.solver_version == 1
            assert config.mainnet is False
            assert config.is_logging is False
            assert config.retry_count == 3
    
    def test_config_with_file(self, temp_dir):
        """Test creating config with file"""
        config_content = """[DYNEX]
api_key = file_key
api_secret = file_secret
api_endpoint = https://file-api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = file-ftp.dynex.dev
ftp_username = file_user
ftp_password = file_pass
"""
        config_path = Path(temp_dir) / "dynex.ini"
        config_path.write_text(config_content)
        
        solver_dir = Path(temp_dir) / "testnet"
        solver_dir.mkdir(exist_ok=True)
        
        # Clear environment variables to test file-only config
        with patch.dict(os.environ, {}, clear=True):
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir),
                mainnet=False
            )
            
            assert config.api_key == 'file_key'
            assert config.api_secret == 'file_secret'
            assert config.api_endpoint == 'https://file-api.dynex.dev'
            assert config.ftp_hostname == 'file-ftp.dynex.dev'
            assert config.ftp_username == 'file_user'
            assert config.ftp_password == 'file_pass'
    
    def test_env_priority_over_file(self, temp_dir):
        """Test that environment variables take priority over file"""
        config_content = """[DYNEX]
api_key = file_key
api_secret = file_secret
api_endpoint = https://file-api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = file-ftp.dynex.dev
ftp_username = file_user
ftp_password = file_pass
"""
        config_path = Path(temp_dir) / "dynex.ini"
        config_path.write_text(config_content)
        
        solver_dir = Path(temp_dir) / "testnet"
        solver_dir.mkdir(exist_ok=True)
        
        # Set only specific environment variables, clear others
        with patch.dict(os.environ, {
            'DYNEX_API_KEY': 'env_key',
            'DYNEX_API_SECRET': 'env_secret',
        }, clear=True):
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir),
                mainnet=False
            )
            
            # Environment variables should take priority
            assert config.api_key == 'env_key'
            assert config.api_secret == 'env_secret'
            # File values should be used for non-env variables
            assert config.api_endpoint == 'https://file-api.dynex.dev'
    
    def test_config_validation(self):
        """Test config validation"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(FileNotFoundError):
                DynexConfig()
    
    def test_solver_version_validation(self, temp_dir):
        """Test solver version validation"""
        # Create config file
        config_content = """[DYNEX]
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
        
        with patch.dict(os.environ, {
            'DYNEX_API_KEY': 'test_key',
            'DYNEX_API_SECRET': 'test_secret',
            'DYNEX_API_ENDPOINT': 'https://test-api.dynex.dev',
            'DYNEX_FTP_HOSTNAME': 'test-ftp.dynex.dev',
            'DYNEX_FTP_USERNAME': 'test_user',
            'DYNEX_FTP_PASSWORD': 'test_pass',
        }):
            # Invalid solver version should default to 2
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir),
                solver_version=3
            )
            assert config.solver_version == 2
            
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir),
                solver_version=1
            )
            assert config.solver_version == 1
    
    def test_as_dict(self, temp_dir):
        """Test as_dict method"""
        # Create config file
        config_content = """[DYNEX]
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
        
        with patch.dict(os.environ, {
            'DYNEX_API_KEY': 'test_key',
            'DYNEX_API_SECRET': 'test_secret',
            'DYNEX_API_ENDPOINT': 'https://test-api.dynex.dev',
            'DYNEX_FTP_HOSTNAME': 'test-ftp.dynex.dev',
            'DYNEX_FTP_USERNAME': 'test_user',
            'DYNEX_FTP_PASSWORD': 'test_pass',
        }):
            config = DynexConfig(
                config_path=str(config_path),
                solver_path=str(solver_dir),
                solver_version=1, 
                mainnet=False
            )
            config_dict = config.as_dict()
            
            assert isinstance(config_dict, dict)
            assert config_dict['API_KEY'] == 'test_key'
            assert config_dict['API_SECRET'] == 'test_secret'
            assert config_dict['solver_version'] == 1
            assert 'solver_path' in config_dict
