"""
Tests for Dynex model classes (BQM, SAT, CQM, DQM)
"""
import pytest
import dimod
from unittest.mock import patch, Mock

from dynex import BQM, SAT, CQM, DQM, DynexConfig


class TestBQM:
    """Test cases for BQM model"""
    
    def test_bqm_creation(self, test_config, sample_bqm):
        """Test creating BQM model"""
        model = BQM(sample_bqm, config=test_config)
        
        assert model.type == 'wcnf'
        assert model.type_str == 'BQM'
        assert hasattr(model, 'clauses')
        assert hasattr(model, 'num_variables')
        assert hasattr(model, 'num_clauses')
        assert hasattr(model, 'var_mappings')
        assert hasattr(model, 'precision')
        assert hasattr(model, 'bqm')
    
    def test_bqm_with_different_formulas(self, test_config, sample_bqm):
        """Test BQM with different formula types"""
        # Test formula=1
        model1 = BQM(sample_bqm, formula=1, config=test_config)
        assert model1.type == 'wcnf'
        
        # Test formula=2 (default)
        model2 = BQM(sample_bqm, formula=2, config=test_config)
        assert model2.type == 'wcnf'
    
    def test_bqm_with_empty_bqm(self, test_config):
        """Test BQM with empty BQM should raise exception"""
        empty_bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)
        
        with pytest.raises(Exception, match="Could not initiate model"):
            BQM(empty_bqm, config=test_config)
    
    def test_bqm_str_representation(self, test_config, sample_bqm):
        """Test string representation of BQM"""
        model = BQM(sample_bqm, config=test_config)
        assert str(model) == 'BQM'


class TestSAT:
    """Test cases for SAT model"""
    
    def test_sat_creation(self, test_config, sample_sat_clauses):
        """Test creating SAT model"""
        model = SAT(sample_sat_clauses, config=test_config)
        
        assert model.type == 'cnf'
        assert model.type_str == 'SAT'
        assert hasattr(model, 'clauses')
        assert hasattr(model, 'wcnf_offset')
        assert hasattr(model, 'precision')
    
    def test_sat_with_empty_clauses(self, test_config):
        """Test SAT with empty clauses"""
        model = SAT([], config=test_config)
        assert model.type == 'cnf'
        assert model.type_str == 'SAT'
    
    def test_sat_str_representation(self, test_config, sample_sat_clauses):
        """Test string representation of SAT"""
        model = SAT(sample_sat_clauses, config=test_config)
        assert str(model) == 'SAT'


class TestCQM:
    """Test cases for CQM model"""
    
    def test_cqm_creation(self, test_config, sample_cqm):
        """Test creating CQM model"""
        model = CQM(sample_cqm, config=test_config)
        
        assert model.type == 'wcnf'
        assert model.type_str == 'CQM'
        assert hasattr(model, 'clauses')
        assert hasattr(model, 'num_variables')
        assert hasattr(model, 'num_clauses')
        assert hasattr(model, 'var_mappings')
        assert hasattr(model, 'precision')
        assert hasattr(model, 'bqm')
        assert hasattr(model, 'invert')
        assert hasattr(model, 'cqm')
    
    def test_cqm_with_different_formulas(self, test_config, sample_cqm):
        """Test CQM with different formula types"""
        # Test formula=1
        model1 = CQM(sample_cqm, formula=1, config=test_config)
        assert model1.type == 'wcnf'
        
        # Test formula=2 (default)
        model2 = CQM(sample_cqm, formula=2, config=test_config)
        assert model2.type == 'wcnf'
    
    def test_cqm_str_representation(self, test_config, sample_cqm):
        """Test string representation of CQM"""
        model = CQM(sample_cqm, config=test_config)
        assert str(model) == 'CQM'


class TestDQM:
    """Test cases for DQM model"""
    
    def test_dqm_creation(self, test_config, sample_dqm):
        """Test creating DQM model"""
        model = DQM(sample_dqm, config=test_config)
        
        assert model.type == 'wcnf'
        assert model.type_str == 'DQM'
        assert hasattr(model, 'clauses')
        assert hasattr(model, 'num_variables')
        assert hasattr(model, 'num_clauses')
        assert hasattr(model, 'var_mappings')
        assert hasattr(model, 'precision')
        assert hasattr(model, 'bqm')
        assert hasattr(model, 'invert')
        assert hasattr(model, 'dqm')
    
    def test_dqm_with_different_formulas(self, test_config, sample_dqm):
        """Test DQM with different formula types"""
        # Test formula=1
        model1 = DQM(sample_dqm, formula=1, config=test_config)
        assert model1.type == 'wcnf'
        
        # Test formula=2 (default)
        model2 = DQM(sample_dqm, formula=2, config=test_config)
        assert model2.type == 'wcnf'
    
    def test_dqm_str_representation(self, test_config, sample_dqm):
        """Test string representation of DQM"""
        model = DQM(sample_dqm, config=test_config)
        assert str(model) == 'DQM'


class TestModelBase:
    """Test cases for base model functionality"""
    
    def test_model_without_config(self, sample_bqm):
        """Test model creation without explicit config"""
        # Should create default config
        model = BQM(sample_bqm)
        assert hasattr(model, 'config')
        assert isinstance(model.config, DynexConfig)
    
    def test_model_precision_calculation(self, test_config, sample_bqm):
        """Test precision calculation in models"""
        model = BQM(sample_bqm, config=test_config)
        assert hasattr(model, 'precision')
        assert model.precision > 0
    
    def test_model_variable_mappings(self, test_config, sample_bqm):
        """Test variable mappings in models"""
        model = BQM(sample_bqm, config=test_config)
        assert hasattr(model, 'var_mappings')
        assert isinstance(model.var_mappings, dict)
    
    def test_model_clauses_generation(self, test_config, sample_bqm):
        """Test clauses generation in models"""
        model = BQM(sample_bqm, config=test_config)
        assert hasattr(model, 'clauses')
        assert isinstance(model.clauses, list)
        assert len(model.clauses) > 0
