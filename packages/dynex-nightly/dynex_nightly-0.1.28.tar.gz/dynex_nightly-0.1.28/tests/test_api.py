"""
Tests for DynexAPI class
"""
import json
from unittest.mock import patch, Mock, MagicMock

import pytest
import requests

from dynex import DynexAPI, DynexConfig


class TestDynexAPI:
    """Test cases for DynexAPI"""
    
    def test_api_creation(self, test_config):
        """Test creating DynexAPI"""
        api = DynexAPI(config=test_config)
        
        assert api.config == test_config
        assert api.logging is False
    
    def test_api_creation_with_logging(self, test_config):
        """Test creating DynexAPI with logging enabled"""
        api = DynexAPI(config=test_config, logging=True)
        
        assert api.config == test_config
        assert api.logging is True
    
    def test_api_creation_without_config(self):
        """Test creating DynexAPI without explicit config"""
        with patch.dict('os.environ', {
            'DYNEX_API_KEY': 'test_key',
            'DYNEX_API_SECRET': 'test_secret',
            'DYNEX_API_ENDPOINT': 'https://test-api.dynex.dev',
            'DYNEX_FTP_HOSTNAME': 'test-ftp.dynex.dev',
            'DYNEX_FTP_USERNAME': 'test_user',
            'DYNEX_FTP_PASSWORD': 'test_pass',
        }):
            api = DynexAPI()
            
            assert hasattr(api, 'config')
            assert isinstance(api.config, DynexConfig)
    
    @patch('requests.post')
    def test_make_base_post_request_success(self, mock_post, test_config):
        """Test successful POST request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api._make_base_post_request(
            "https://test-api.dynex.dev/test",
            {"data": "test"}
        )
        
        assert result == {"status": "success"}
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_make_base_post_request_failure(self, mock_post, test_config):
        """Test failed POST request"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        with pytest.raises(Exception, match="Error code: 400"):
            api._make_base_post_request(
                "https://test-api.dynex.dev/test",
                {"data": "test"}
            )
    
    @patch('requests.post')
    def test_update_job_api(self, mock_post, test_config):
        """Test update job API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"job_id": 12345, "status": "updated"}
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.update_job_api(12345)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_report_invalid(self, mock_post, test_config):
        """Test report invalid solution API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "reported"}
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.report_invalid("test_file.dnx", "wrong energy")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_create_job_api(self, mock_post, test_config):
        """Test create job API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": 12345,
            "filename": "test_file.dnx",
            "price_per_block": 0.001,
            "qasm": None
        }
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        # Mock the sampler object
        mock_sampler = Mock()
        mock_sampler.filename = "test_file.dnx"
        mock_sampler.num_variables = 10
        mock_sampler.num_clauses = 20
        
        result = api.create_job_api(
            sampler=mock_sampler,
            annealing_time=100,
            switchfraction=0.0,
            num_reads=32,
            alpha=20,
            beta=20,
            gamma=1,
            delta=1,
            epsilon=1,
            zeta=1,
            minimum_stepsize=0.05,
            block_fee=0,
            is_cluster=True,
            cluster_type=1,
            shots=1,
            rank=1
        )
        
        assert result == (12345, "test_file.dnx", 0.001, None)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_finish_job_api(self, mock_post, test_config):
        """Test finish job API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "finished"}
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.finish_job_api(12345, 0, 0.0)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_cancel_job_api(self, mock_post, test_config):
        """Test cancel job API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "cancelled"}
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.cancel_job_api(12345)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_get_status_details_api(self, mock_post, test_config):
        """Test get status details API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "loc_min": 0,
            "energy_min": -2.5,
            "mallob_chips": 100,
            "details": "Test details"
        }
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.get_status_details_api(12345, 100)
        
        assert result == (0, -2.5, 100, "Test details")
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_account_status(self, mock_post, test_config):
        """Test account status API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "active",
            "balance": 1000.0,
            "jobs_completed": 50
        }
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.account_status()
        
        assert result["status"] == "active"
        assert result["balance"] == 1000.0
        assert result["jobs_completed"] == 50
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_estimate_costs(self, mock_post, test_config):
        """Test estimate costs API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "estimated_cost": 0.05,
            "currency": "DNX",
            "breakdown": {
                "base_cost": 0.03,
                "complexity_factor": 0.02
            }
        }
        mock_post.return_value = mock_response
        
        api = DynexAPI(config=test_config)
        
        result = api.estimate_costs(
            num_variables=100,
            num_clauses=500,
            annealing_time=1000
        )
        
        assert result["estimated_cost"] == 0.05
        assert result["currency"] == "DNX"
        mock_post.assert_called_once()
    
    def test_post_request_with_file(self, test_config, temp_dir):
        """Test POST request with file upload"""
        # Create a test file
        test_file = temp_dir / "test.dnx"
        test_file.write_text("test content")
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "uploaded"}
            mock_post.return_value = mock_response
            
            api = DynexAPI(config=test_config)
            
            result = DynexAPI._post_request(
                "https://test-api.dynex.dev/upload",
                {"job_id": 12345},
                str(test_file)
            )
            
            assert result.status_code == 200
            mock_post.assert_called_once()
            
            # Check that files were passed correctly
            call_args = mock_post.call_args
            assert 'files' in call_args[1]
            assert 'opts' in call_args[1]['files']
            assert 'job' in call_args[1]['files']
