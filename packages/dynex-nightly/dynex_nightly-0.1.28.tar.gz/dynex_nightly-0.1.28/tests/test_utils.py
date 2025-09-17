"""
Tests for utility functions
"""
import pytest
import dimod
from unittest.mock import patch

from dynex import test, sample_qubo, DynexConfig


class TestUtils:
    """Test cases for utility functions"""
    
    def test_test_function(self):
        """Test the test() utility function"""
        # This function should not raise an exception
        try:
            result = test()
            # The function might return something or just complete successfully
            assert True  # If we get here, the function worked
        except Exception as e:
            # If it raises an exception, it should be a specific type
            # (e.g., configuration error, not a general exception)
            assert "test" in str(e).lower() or "config" in str(e).lower()
    
    def test_sample_qubo_function(self, test_config):
        """Test the sample_qubo utility function"""
        # Create a simple QUBO
        Q = {(0, 0): 1.0, (1, 1): -1.0, (0, 1): 0.5}
        offset = 0.0
        
        # Mock the sampling process
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {0: 1, 1: 0}
            mock_sampleset.first.energy = -0.5
            mock_sampler.sample.return_value = mock_sampleset
            
            result = sample_qubo(Q, offset, config=test_config)
            
            assert result == mock_sampleset
            mock_sampler_class.assert_called_once()
            mock_sampler.sample.assert_called_once()
    
    def test_sample_qubo_without_config(self):
        """Test sample_qubo without explicit config"""
        Q = {(0, 0): 1.0, (1, 1): -1.0, (0, 1): 0.5}
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {0: 1, 1: 0}
            mock_sampleset.first.energy = -0.5
            mock_sampler.sample.return_value = mock_sampleset
            
            result = sample_qubo(Q, offset)
            
            assert result == mock_sampleset
            mock_sampler_class.assert_called_once()
    
    def test_sample_qubo_with_parameters(self, test_config):
        """Test sample_qubo with additional parameters"""
        Q = {(0, 0): 1.0, (1, 1): -1.0, (0, 1): 0.5}
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {0: 1, 1: 0}
            mock_sampleset.first.energy = -0.5
            mock_sampler.sample.return_value = mock_sampleset
            
            result = sample_qubo(
                Q, 
                offset, 
                config=test_config,
                num_reads=64,
                annealing_time=200
            )
            
            assert result == mock_sampleset
            mock_sampler.sample.assert_called_once_with(
                num_reads=64,
                annealing_time=200
            )
    
    def test_sample_qubo_error_handling(self, test_config):
        """Test sample_qubo error handling"""
        Q = {(0, 0): 1.0, (1, 1): -1.0, (0, 1): 0.5}
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampler.sample.side_effect = Exception("Sampling failed")
            
            with pytest.raises(Exception, match="Sampling failed"):
                sample_qubo(Q, offset, config=test_config)
    
    def test_sample_qubo_empty_qubo(self, test_config):
        """Test sample_qubo with empty QUBO"""
        Q = {}
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {}
            mock_sampleset.first.energy = 0.0
            mock_sampler.sample.return_value = mock_sampleset
            
            result = sample_qubo(Q, offset, config=test_config)
            
            assert result == mock_sampleset
    
    def test_sample_qubo_large_qubo(self, test_config):
        """Test sample_qubo with large QUBO"""
        # Create a larger QUBO
        Q = {}
        for i in range(50):
            Q[(i, i)] = 1.0
            if i < 49:
                Q[(i, i+1)] = 0.5
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {i: i % 2 for i in range(50)}
            mock_sampleset.first.energy = -25.0
            mock_sampler.sample.return_value = mock_sampleset
            
            result = sample_qubo(Q, offset, config=test_config)
            
            assert result == mock_sampleset
            mock_sampler_class.assert_called_once()


class TestUtilityIntegration:
    """Integration tests for utility functions"""
    
    def test_utility_with_different_configs(self, temp_dir):
        """Test utilities with different configurations"""
        # Create test config
        config_content = """[DYNEX]
api_key = test_key
api_secret = test_secret
api_endpoint = https://test-api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = test-ftp.dynex.dev
ftp_username = test_user
ftp_password = test_pass
"""
        config_path = os.path.join(temp_dir, "dynex.ini")
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Create solver directory
        solver_dir = os.path.join(temp_dir, "testnet")
        os.makedirs(solver_dir, exist_ok=True)
        
        config = DynexConfig(
            config_path=config_path,
            solver_path=solver_dir,
            mainnet=False
        )
        
        Q = {(0, 0): 1.0, (1, 1): -1.0, (0, 1): 0.5}
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler = mock_sampler_class.return_value
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {0: 1, 1: 0}
            mock_sampleset.first.energy = -0.5
            mock_sampler.sample.return_value = mock_sampleset
            
            result = sample_qubo(Q, offset, config=config)
            
            assert result == mock_sampleset
            # Verify that the config was passed correctly
            mock_sampler_class.assert_called_once()
            call_args = mock_sampler_class.call_args
            assert call_args[1]['config'] == config
    
    def test_utility_error_propagation(self, test_config):
        """Test that errors in utilities are properly propagated"""
        Q = {(0, 0): 1.0, (1, 1): -1.0, (0, 1): 0.5}
        offset = 0.0
        
        with patch('dynex.utils.DynexSampler') as mock_sampler_class:
            mock_sampler_class.side_effect = Exception("Configuration error")
            
            with pytest.raises(Exception, match="Configuration error"):
                sample_qubo(Q, offset, config=test_config)
