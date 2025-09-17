"""
Integration tests for Dynex SDK
"""
import pytest
import dimod
from unittest.mock import patch, Mock
import tempfile
import os

from dynex import DynexSampler, BQM, SAT, CQM, DQM, DynexConfig, DynexAPI


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_bqm_workflow(self, test_config, sample_bqm):
        """Test complete BQM workflow"""
        # Create model
        model = BQM(sample_bqm, config=test_config)
        assert model.type == 'wcnf'
        
        # Create sampler
        sampler = DynexSampler(model, config=test_config)
        assert sampler.model == model
        
        # Test sampling (mocked)
        with patch('dynex.sampler._DynexSampler') as mock_internal:
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {'x1': 1, 'x2': 0, 'x3': 1}
            mock_sampleset.first.energy = -2.5
            mock_internal.return_value.sample.return_value = mock_sampleset
            
            result = sampler.sample(num_reads=32, annealing_time=100)
            
            assert result == mock_sampleset
    
    def test_sat_workflow(self, test_config, sample_sat_clauses):
        """Test complete SAT workflow"""
        # Create model
        model = SAT(sample_sat_clauses, config=test_config)
        assert model.type == 'cnf'
        
        # Create sampler
        sampler = DynexSampler(model, config=test_config)
        assert sampler.model == model
        
        # Test sampling (mocked)
        with patch('dynex.sampler._DynexSampler') as mock_internal:
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {1: 1, 2: 0, 3: 1}
            mock_sampleset.first.energy = 0.0
            mock_internal.return_value.sample.return_value = mock_sampleset
            
            result = sampler.sample(num_reads=32, annealing_time=100)
            
            assert result == mock_sampleset
    
    def test_cqm_workflow(self, test_config, sample_cqm):
        """Test complete CQM workflow"""
        # Create model
        model = CQM(sample_cqm, config=test_config)
        assert model.type == 'wcnf'
        
        # Create sampler
        sampler = DynexSampler(model, config=test_config)
        assert sampler.model == model
        
        # Test sampling (mocked)
        with patch('dynex.sampler._DynexSampler') as mock_internal:
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {'num_widget_a': 3, 'num_widget_b': 2}
            mock_sampleset.first.energy = -17.0
            mock_internal.return_value.sample.return_value = mock_sampleset
            
            result = sampler.sample(num_reads=32, annealing_time=100)
            
            assert result == mock_sampleset
    
    def test_dqm_workflow(self, test_config, sample_dqm):
        """Test complete DQM workflow"""
        # Create model
        model = DQM(sample_dqm, config=test_config)
        assert model.type == 'wcnf'
        
        # Create sampler
        sampler = DynexSampler(model, config=test_config)
        assert sampler.model == model
        
        # Test sampling (mocked)
        with patch('dynex.sampler._DynexSampler') as mock_internal:
            mock_sampleset = Mock()
            mock_sampleset.first.sample = {'my_hand': 0, 'their_hand': 1}
            mock_sampleset.first.energy = -1.0
            mock_internal.return_value.sample.return_value = mock_sampleset
            
            result = sampler.sample(num_reads=32, annealing_time=100)
            
            assert result == mock_sampleset
    
    def test_config_environment_priority(self, temp_dir):
        """Test that environment variables take priority over config file"""
        # Create config file
        config_content = """[DYNEX]
api_key = file_key
api_secret = file_secret
api_endpoint = https://file-api.dynex.dev

[FTP_SOLUTION_FILES]
ftp_hostname = file-ftp.dynex.dev
ftp_username = file_user
ftp_password = file_pass
"""
        config_path = os.path.join(temp_dir, "dynex.ini")
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Create solver directory
        solver_dir = os.path.join(temp_dir, "testnet")
        os.makedirs(solver_dir, exist_ok=True)
        
        # Set environment variables
        env_vars = {
            'DYNEX_API_KEY': 'env_key',
            'DYNEX_API_SECRET': 'env_secret',
        }
        
        with patch.dict(os.environ, env_vars):
            config = DynexConfig(
                config_path=config_path,
                solver_path=solver_dir,
                mainnet=False
            )
            
            # Environment should take priority
            assert config.api_key == 'env_key'
            assert config.api_secret == 'env_secret'
            # File values should be used for others
            assert config.api_endpoint == 'https://file-api.dynex.dev'
    
    def test_solver_version_compatibility(self, test_config, sample_bqm):
        """Test compatibility with different solver versions"""
        # Test solver version 1
        config_v1 = DynexConfig(
            solver_version=1,
            mainnet=False,
            is_logging=False
        )
        config_v1.api_key = test_config.api_key
        config_v1.api_secret = test_config.api_secret
        config_v1.api_endpoint = test_config.api_endpoint
        config_v1.ftp_hostname = test_config.ftp_hostname
        config_v1.ftp_username = test_config.ftp_username
        config_v1.ftp_password = test_config.ftp_password
        config_v1.solver_path = test_config.solver_path
        
        model_v1 = BQM(sample_bqm, config=config_v1)
        assert model_v1.type == 'wcnf'
        
        # Test solver version 2
        config_v2 = DynexConfig(
            solver_version=2,
            mainnet=False,
            is_logging=False
        )
        config_v2.api_key = test_config.api_key
        config_v2.api_secret = test_config.api_secret
        config_v2.api_endpoint = test_config.api_endpoint
        config_v2.ftp_hostname = test_config.ftp_hostname
        config_v2.ftp_username = test_config.ftp_username
        config_v2.ftp_password = test_config.ftp_password
        config_v2.solver_path = test_config.solver_path
        
        model_v2 = BQM(sample_bqm, config=config_v2)
        assert model_v2.type == 'wcnf'
    
    def test_error_handling(self, test_config):
        """Test error handling in various scenarios"""
        # Test with invalid BQM
        with pytest.raises(Exception):
            empty_bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)
            BQM(empty_bqm, config=test_config)
        
        # Test sampler with invalid model type
        mock_model = Mock()
        mock_model.type = 'invalid'
        
        with pytest.raises(Exception):
            DynexSampler(mock_model, config=test_config)
    
    def test_file_operations(self, test_config, sample_bqm, temp_dir):
        """Test file operations in sampling"""
        model = BQM(sample_bqm, config=test_config)
        
        with patch('os.path.isfile', return_value=True):
            with patch('os.getcwd', return_value=temp_dir):
                sampler = DynexSampler(model, config=test_config)
                
                # Check that tmp directory was created
                tmp_dir = os.path.join(temp_dir, 'tmp')
                assert os.path.exists(tmp_dir)
                
                # Test file creation
                with patch('dynex.sampler._DynexSampler') as mock_internal:
                    mock_sampleset = Mock()
                    mock_internal.return_value.sample.return_value = mock_sampleset
                    
                    result = sampler.sample(num_reads=32, annealing_time=100)
                    assert result == mock_sampleset


class TestPerformance:
    """Performance-related tests"""
    
    def test_large_bqm_handling(self, test_config):
        """Test handling of large BQM"""
        # Create a larger BQM
        large_bqm = dimod.BinaryQuadraticModel(
            {i: 1.0 for i in range(100)},
            {(i, i+1): 0.5 for i in range(99)},
            0.0,
            dimod.BINARY
        )
        
        model = BQM(large_bqm, config=test_config)
        assert model.num_variables == 100
        assert model.num_clauses > 0
    
    def test_memory_usage(self, test_config, sample_bqm):
        """Test memory usage with multiple models"""
        models = []
        for i in range(10):
            model = BQM(sample_bqm, config=test_config)
            models.append(model)
        
        assert len(models) == 10
        for model in models:
            assert model.type == 'wcnf'


class TestConcurrency:
    """Test concurrent operations"""
    
    def test_multiple_samplers(self, test_config, sample_bqm):
        """Test creating multiple samplers"""
        model = BQM(sample_bqm, config=test_config)
        
        samplers = []
        for i in range(5):
            sampler = DynexSampler(model, config=test_config, description=f'Job {i}')
            samplers.append(sampler)
        
        assert len(samplers) == 5
        for i, sampler in enumerate(samplers):
            assert sampler.description == f'Job {i}'
    
    def test_thread_safety(self, test_config, sample_bqm):
        """Test thread safety of configuration"""
        import threading
        import time
        
        results = []
        
        def create_model():
            time.sleep(0.01)  # Simulate some work
            model = BQM(sample_bqm, config=test_config)
            results.append(model.type)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_model)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) == 10
        assert all(result == 'wcnf' for result in results)
