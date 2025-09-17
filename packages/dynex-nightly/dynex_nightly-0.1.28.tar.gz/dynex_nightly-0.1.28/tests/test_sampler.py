"""
Tests for DynexSampler class
"""
import pytest
import dimod
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os

from dynex import DynexSampler, BQM, SAT, DynexConfig


class TestDynexSampler:
    """Test cases for DynexSampler"""
    
    def test_sampler_creation(self, test_config, sample_bqm):
        """Test creating DynexSampler"""
        model = BQM(sample_bqm, config=test_config)
        sampler = DynexSampler(model, config=test_config)
        
        assert sampler.model == model
        assert sampler.config == test_config
        assert sampler.state == 'initialised'
        assert sampler.description == 'Dynex SDK Job'
        assert sampler.bnb is True
    
    def test_sampler_creation_with_parameters(self, test_config, sample_bqm):
        """Test creating DynexSampler with custom parameters"""
        model = BQM(sample_bqm, config=test_config)
        sampler = DynexSampler(
            model,
            config=test_config,
            description='Custom Job',
            bnb=False
        )
        
        assert sampler.description == 'Custom Job'
        assert sampler.bnb is False
    
    def test_sampler_without_config(self, sample_bqm):
        """Test creating sampler without explicit config"""
        model = BQM(sample_bqm)
        sampler = DynexSampler(model)
        
        assert hasattr(sampler, 'config')
        assert isinstance(sampler.config, DynexConfig)
    
    @patch('dynex.sampler._DynexSampler')
    def test_sampler_sample_single(self, mock_internal_sampler, test_config, sample_bqm):
        """Test sampling with single clone"""
        # Setup mock
        mock_sampleset = Mock()
        mock_sampleset.first.sample = {'x1': 1, 'x2': 0, 'x3': 1}
        mock_sampleset.first.energy = -2.5
        mock_internal_sampler.return_value.sample.return_value = mock_sampleset
        
        model = BQM(sample_bqm, config=test_config)
        sampler = DynexSampler(model, config=test_config)
        
        result = sampler.sample(num_reads=32, annealing_time=100)
        
        assert result == mock_sampleset
        mock_internal_sampler.return_value.sample.assert_called_once()
    
    @patch('dynex.sampler.multiprocessing.Process')
    @patch('dynex.sampler.multiprocessing.Queue')
    def test_sampler_sample_with_clones(self, mock_queue, mock_process, test_config, sample_bqm):
        """Test sampling with multiple clones"""
        # Setup mocks
        mock_sampleset = Mock()
        mock_sampleset.first.sample = {'x1': 1, 'x2': 0, 'x3': 1}
        mock_sampleset.first.energy = -2.5
        
        mock_queue_instance = Mock()
        mock_queue_instance.get.return_value = mock_sampleset
        mock_queue.return_value = mock_queue_instance
        
        mock_process_instance = Mock()
        mock_process_instance.is_alive.return_value = False
        mock_process.return_value = mock_process_instance
        
        # Mock the internal sampler
        with patch('dynex.sampler._DynexSampler') as mock_internal:
            mock_internal.return_value.sample.return_value = mock_sampleset
            
            model = BQM(sample_bqm, config=test_config)
            sampler = DynexSampler(model, config=test_config)
            
            result = sampler.sample(num_reads=32, annealing_time=100, clones=2)
            
            assert result == mock_sampleset
            assert mock_process.call_count == 2  # Two clones
    
    def test_sampler_sample_parameter_validation(self, test_config, sample_bqm):
        """Test parameter validation in sample method"""
        model = BQM(sample_bqm, config=test_config)
        sampler = DynexSampler(model, config=test_config)
        
        # Test invalid clones parameter
        with pytest.raises(Exception, match="Value of clones must be in range"):
            sampler.sample(clones=0)
        
        with pytest.raises(Exception, match="Value of clones must be in range"):
            sampler.sample(clones=129)
    
    def test_sampler_sample_testnet_clones_restriction(self, test_config, sample_bqm):
        """Test that clones > 1 only work on mainnet"""
        # Set mainnet=False
        test_config.mainnet = False
        
        model = BQM(sample_bqm, config=test_config)
        sampler = DynexSampler(model, config=test_config)
        
        with pytest.raises(Exception, match="Clone sampling is only supported on the mainnet"):
            sampler.sample(clones=2)
    
    @patch('dynex.sampler._DynexSampler')
    def test_sampler_sample_with_all_parameters(self, mock_internal_sampler, test_config, sample_bqm):
        """Test sampling with all available parameters"""
        mock_sampleset = Mock()
        mock_internal_sampler.return_value.sample.return_value = mock_sampleset
        
        model = BQM(sample_bqm, config=test_config)
        sampler = DynexSampler(model, config=test_config)
        
        result = sampler.sample(
            num_reads=64,
            annealing_time=200,
            clones=1,
            switchfraction=0.1,
            alpha=30,
            beta=30,
            gamma=2,
            delta=2,
            epsilon=2,
            zeta=2,
            minimum_stepsize=0.01,
            debugging=True,
            block_fee=1000,
            is_cluster=True,
            shots=2,
            rank=2,
            cluster_type=2,
            preprocess=True
        )
        
        assert result == mock_sampleset
        mock_internal_sampler.return_value.sample.assert_called_once_with(
            num_reads=64,
            annealing_time=200,
            switchfraction=0.1,
            alpha=30,
            beta=30,
            gamma=2,
            delta=2,
            epsilon=2,
            zeta=2,
            minimum_stepsize=0.01,
            debugging=True,
            block_fee=1000,
            is_cluster=True,
            shots=2,
            rank=2,
            cluster_type=2,
            preprocess=True
        )


class TestDynexSamplerInternal:
    """Test cases for internal DynexSampler functionality"""
    
    def test_internal_sampler_creation(self, test_config, sample_bqm):
        """Test creating internal sampler"""
        model = BQM(sample_bqm, config=test_config)
        
        with patch('os.path.isfile', return_value=True):
            from dynex.sampler import _DynexSampler
            sampler = _DynexSampler(
                model, 
                logging=True, 
                mainnet=False, 
                description='Test Job',
                test=True,
                config=test_config
            )
            
            assert sampler.model == model
            assert sampler.config == test_config
            assert sampler.description == 'Test Job'
    
    def test_internal_sampler_invalid_model_type(self, test_config):
        """Test internal sampler with invalid model type"""
        # Create a mock model with invalid type
        mock_model = Mock()
        mock_model.type = 'invalid'
        
        with patch('os.path.isfile', return_value=True):
            from dynex.sampler import _DynexSampler
            with pytest.raises(Exception, match="INCORRECT MODEL TYPE"):
                _DynexSampler(
                    mock_model,
                    logging=True,
                    mainnet=False,
                    description='Test Job',
                    test=True,
                    config=test_config
                )
    
    def test_internal_sampler_file_creation(self, test_config, sample_bqm, temp_dir):
        """Test file creation in internal sampler"""
        model = BQM(sample_bqm, config=test_config)
        
        with patch('os.path.isfile', return_value=True):
            with patch('os.getcwd', return_value=temp_dir):
                from dynex.sampler import _DynexSampler
                sampler = _DynexSampler(
                    model,
                    logging=True,
                    mainnet=False,
                    description='Test Job',
                    test=True,
                    config=test_config
                )
                
                # Check that filename was generated
                assert hasattr(sampler, 'filename')
                assert sampler.filename.endswith('.dnx')
                
                # Check that file was created
                file_path = os.path.join(temp_dir, 'tmp', sampler.filename)
                assert os.path.exists(file_path)


class TestSamplerUtilities:
    """Test cases for sampler utility functions"""
    
    def test_to_wcnf_string(self, test_config, sample_bqm):
        """Test to_wcnf_string utility function"""
        from dynex.sampler import to_wcnf_string
        
        clauses = [[1, -2, 3], [-1, 4, 5]]
        num_variables = 5
        num_clauses = 2
        
        result = to_wcnf_string(clauses, num_variables, num_clauses)
        
        assert "p wcnf 5 2" in result
        assert "1 -2 3 0" in result
        assert "-1 4 5 0" in result
    
    def test_check_list_length(self, test_config, sample_bqm):
        """Test _check_list_length utility function"""
        from dynex.sampler import _DynexSampler
        
        # Test with k-SAT (clauses longer than 3)
        k_sat_clauses = [[1, 2, 3, 4], [5, 6, 7, 8]]
        assert _DynexSampler._check_list_length(k_sat_clauses) is True
        
        # Test with 3-SAT
        sat3_clauses = [[1, 2, 3], [4, 5, 6]]
        assert _DynexSampler._check_list_length(sat3_clauses) is False
