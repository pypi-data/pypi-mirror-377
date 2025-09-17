# Dynex SDK Tests

This directory contains comprehensive tests for the Dynex SDK library.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_config.py           # Tests for DynexConfig class
├── test_models.py           # Tests for model classes (BQM, SAT, CQM, DQM)
├── test_sampler.py          # Tests for DynexSampler class
├── test_api.py              # Tests for DynexAPI class
├── test_integration.py      # Integration tests
├── test_utils.py            # Tests for utility functions
├── test_runner.py           # Custom test runner script
├── test_config.ini          # Test configuration file
└── README.md                # This file
```

## Running Tests

### Prerequisites

1. Install the package in development mode:
   ```bash
   pip install -e .
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Quick Start

Run all tests:
```bash
make test
```

Or using pytest directly:
```bash
pytest tests/ -v
```

### Test Categories

#### Unit Tests
Test individual components in isolation:
```bash
make test-unit
# or
pytest tests/ -v -m "not integration"
```

#### Integration Tests
Test complete workflows and component interactions:
```bash
make test-integration
# or
pytest tests/test_integration.py -v -m integration
```

#### Coverage Tests
Run tests with coverage reporting:
```bash
make test-coverage
# or
pytest tests/ -v --cov=dynex --cov-report=html
```

### Using the Test Runner

The custom test runner provides additional functionality:

```bash
# Run all tests
python tests/test_runner.py --all

# Run with coverage
python tests/test_runner.py --all --coverage --html

# Run specific test types
python tests/test_runner.py --basic
python tests/test_runner.py --pytest
python tests/test_runner.py --integration

# Run with specific markers
python tests/test_runner.py --pytest --markers "not slow"
```

## Test Configuration

### Environment Variables

Tests use environment variables for configuration. The following are set automatically in test fixtures:

```bash
DYNEX_API_KEY=test_key_12345
DYNEX_API_SECRET=test_secret_67890
DYNEX_API_ENDPOINT=https://test-api.dynex.dev
DYNEX_FTP_HOSTNAME=test-ftp.dynex.dev
DYNEX_FTP_USERNAME=test_user
DYNEX_FTP_PASSWORD=test_password
```

### Configuration File

A test configuration file is available at `tests/test_config.ini` for file-based configuration testing.

## Test Fixtures

### Available Fixtures

- `test_config`: Pre-configured DynexConfig for testing
- `mock_api`: Mocked DynexAPI for network-free testing
- `sample_bqm`: Sample BinaryQuadraticModel for testing
- `sample_sat_clauses`: Sample SAT clauses for testing
- `sample_cqm`: Sample ConstrainedQuadraticModel for testing
- `sample_dqm`: Sample DiscreteQuadraticModel for testing
- `temp_dir`: Temporary directory for file operations
- `setup_logging`: Logging configuration for tests

### Using Fixtures

```python
def test_my_function(test_config, sample_bqm):
    model = BQM(sample_bqm, config=test_config)
    # Test the model...
```

## Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Test Structure

```python
class TestMyClass:
    """Test cases for MyClass"""
    
    def test_basic_functionality(self, test_config):
        """Test basic functionality"""
        # Arrange
        model = BQM(sample_bqm, config=test_config)
        
        # Act
        result = model.some_method()
        
        # Assert
        assert result is not None
        assert result.type == 'expected_type'
    
    def test_error_handling(self, test_config):
        """Test error handling"""
        with pytest.raises(ValueError, match="Expected error message"):
            # Code that should raise an error
            pass
```

### Mocking

Use mocks for external dependencies:

```python
@patch('dynex.api.requests.post')
def test_api_call(mock_post, test_config):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_post.return_value = mock_response
    
    api = DynexAPI(config=test_config)
    result = api.some_method()
    
    assert result is True
```

## CI/CD Integration

### GitHub Actions

Tests are automatically run on GitHub Actions for:
- Multiple Python versions (3.11, 3.12)
- Multiple operating systems (Ubuntu, Windows, macOS)
- Code quality checks (linting, formatting)
- Coverage reporting

### Local CI

Run the same checks locally:

```bash
make ci-test
```

This runs:
- Code formatting checks
- Linting
- All tests with coverage
- Integration tests

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -v -s
```

### Specific Test

```bash
pytest tests/test_models.py::TestBQM::test_bqm_creation -v
```

### Debug Mode

```bash
pytest tests/ --pdb
```

### Coverage Details

```bash
pytest tests/ --cov=dynex --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Data

### Sample Models

The test fixtures provide various sample models:

- **BQM**: Simple binary quadratic model with 3 variables
- **SAT**: 3-SAT clauses for satisfiability testing
- **CQM**: Constrained quadratic model with integer variables
- **DQM**: Discrete quadratic model for categorical variables

### Mock Data

Tests use mocked API responses to avoid network dependencies:

```python
mock_response = {
    "job_id": 12345,
    "filename": "test_file.dnx",
    "price_per_block": 0.001,
    "qasm": None
}
```

## Troubleshooting

### Common Issues

1. **Configuration Errors**: Ensure test environment variables are set
2. **Import Errors**: Make sure the package is installed in development mode
3. **File Permission Errors**: Check that test directories are writable
4. **Timeout Errors**: Some tests may timeout on slow systems

### Debug Commands

```bash
# Check configuration
python -c "from dynex import DynexConfig; print(DynexConfig())"

# Test basic functionality
python -c "import dynex; dynex.test()"

# Check test environment
python tests/test_runner.py --basic
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use appropriate fixtures
3. Add docstrings explaining what each test does
4. Include both positive and negative test cases
5. Mock external dependencies
6. Update this README if adding new test categories

## Performance

### Test Speed

- Unit tests: ~1-2 seconds
- Integration tests: ~5-10 seconds
- Full test suite: ~30-60 seconds

### Optimization

- Use `pytest-xdist` for parallel test execution
- Mark slow tests with `@pytest.mark.slow`
- Use `pytest-mock` for efficient mocking
- Cache expensive fixtures with `scope="session"`
