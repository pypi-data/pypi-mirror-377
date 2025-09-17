# Testing Guide for Dynex SDK

This guide explains how to test the Dynex SDK library, including setup, running tests, and CI/CD integration.

## Quick Start

### 1. Install Dependencies

```bash
# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Run Quick Test

```bash
# Run a simple test to verify everything works
python quick_test.py
```

### 3. Run Full Test Suite

```bash
# Run all tests
make test

# Or using pytest directly
pytest tests/ -v
```

## Test Structure

The test suite is organized into several categories:

### Unit Tests
- **`test_config.py`**: Tests for `DynexConfig` class
- **`test_models.py`**: Tests for model classes (`BQM`, `SAT`, `CQM`, `DQM`)
- **`test_sampler.py`**: Tests for `DynexSampler` class
- **`test_api.py`**: Tests for `DynexAPI` class
- **`test_utils.py`**: Tests for utility functions

### Integration Tests
- **`test_integration.py`**: End-to-end workflow tests

### Test Configuration
- **`conftest.py`**: Pytest configuration and shared fixtures
- **`test_config.ini`**: Test configuration file
- **`test_runner.py`**: Custom test runner script

## Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage
make test-coverage

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestBQM::test_bqm_creation -v
```

### Using the Test Runner

```bash
# Run all tests with coverage
python tests/test_runner.py --all --coverage --html

# Run only basic tests
python tests/test_runner.py --basic

# Run with specific markers
python tests/test_runner.py --pytest --markers "not slow"
```

### Advanced Options

```bash
# Run tests in parallel
pytest tests/ -n auto

# Run tests with specific markers
pytest tests/ -m "not slow"

# Run tests with debugging
pytest tests/ --pdb

# Run tests with verbose output
pytest tests/ -v -s

# Run tests with coverage and HTML report
pytest tests/ --cov=dynex --cov-report=html
```

## Test Configuration

### Environment Variables

Tests automatically set the following environment variables:

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

### Mocking

Tests use extensive mocking to avoid network dependencies:

- **API calls**: Mocked using `unittest.mock.patch`
- **File operations**: Use temporary directories
- **External services**: Completely mocked

## Writing Tests

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

### Available Fixtures

- `test_config`: Pre-configured `DynexConfig` for testing
- `mock_api`: Mocked `DynexAPI` for network-free testing
- `sample_bqm`: Sample `BinaryQuadraticModel` for testing
- `sample_sat_clauses`: Sample SAT clauses for testing
- `sample_cqm`: Sample `ConstrainedQuadraticModel` for testing
- `sample_dqm`: Sample `DiscreteQuadraticModel` for testing
- `temp_dir`: Temporary directory for file operations

### Mocking Examples

```python
@patch('dynex.api.requests.post')
def test_api_call(mock_post, test_config):
    """Test API call with mocked response"""
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

The repository includes GitHub Actions workflows that run:

- Tests on multiple Python versions (3.11, 3.12)
- Tests on multiple operating systems (Ubuntu, Windows, macOS)
- Code quality checks (linting, formatting)
- Coverage reporting
- Configuration testing

### Local CI

Run the same checks locally:

```bash
# Run all CI checks
make ci-test

# Run specific checks
make lint          # Code linting
make format-check  # Code formatting
make test-coverage # Tests with coverage
```

### Pre-commit Hooks

Set up pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Debugging Tests

### Common Issues

1. **Configuration Errors**
   ```bash
   # Check configuration
   python -c "from dynex import DynexConfig; print(DynexConfig())"
   ```

2. **Import Errors**
   ```bash
   # Check imports
   python -c "import dynex; print('Imports OK')"
   ```

3. **File Permission Errors**
   ```bash
   # Check test directories
   ls -la tests/tmp tests/testnet
   ```

### Debug Commands

```bash
# Run with debugging
pytest tests/ --pdb

# Run specific test with debugging
pytest tests/test_models.py::TestBQM::test_bqm_creation --pdb

# Run with verbose output
pytest tests/ -v -s

# Check test discovery
pytest --collect-only tests/
```

### Coverage Analysis

```bash
# Generate coverage report
pytest tests/ --cov=dynex --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Performance Testing

### Test Speed

- **Unit tests**: ~1-2 seconds
- **Integration tests**: ~5-10 seconds
- **Full test suite**: ~30-60 seconds

### Optimization

```bash
# Run tests in parallel
pytest tests/ -n auto

# Run only fast tests
pytest tests/ -m "not slow"

# Run specific test categories
pytest tests/test_models.py tests/test_config.py
```

## Test Data

### Sample Models

The test fixtures provide various sample models:

- **BQM**: Simple binary quadratic model with 3 variables
- **SAT**: 3-SAT clauses for satisfiability testing
- **CQM**: Constrained quadratic model with integer variables
- **DQM**: Discrete quadratic model for categorical variables

### Mock Data

Tests use mocked API responses:

```python
mock_response = {
    "job_id": 12345,
    "filename": "test_file.dnx",
    "price_per_block": 0.001,
    "qasm": None
}
```

## Contributing

### Adding New Tests

1. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

2. **Use appropriate fixtures**:
   ```python
   def test_my_function(test_config, sample_bqm):
       # Use provided fixtures
   ```

3. **Add docstrings**:
   ```python
   def test_my_function(self, test_config):
       """Test that my function works correctly"""
   ```

4. **Include both positive and negative cases**:
   ```python
   def test_success_case(self, test_config):
       # Test successful execution
   
   def test_error_case(self, test_config):
       # Test error handling
   ```

5. **Mock external dependencies**:
   ```python
   @patch('external.dependency')
   def test_with_mock(self, mock_dependency):
       # Test with mocked dependency
   ```

### Test Guidelines

- **One assertion per test**: Each test should verify one specific behavior
- **Descriptive names**: Test names should clearly describe what is being tested
- **Independent tests**: Tests should not depend on each other
- **Clean setup/teardown**: Use fixtures for setup and cleanup
- **Mock external dependencies**: Avoid network calls and file system operations

## Troubleshooting

### Test Failures

1. **Check environment variables**:
   ```bash
   env | grep DYNEX
   ```

2. **Verify package installation**:
   ```bash
   pip list | grep dynex
   ```

3. **Check test configuration**:
   ```bash
   python tests/test_runner.py --basic
   ```

4. **Run with verbose output**:
   ```bash
   pytest tests/ -v -s
   ```

### Common Error Messages

- **`FileNotFoundError: Config file not found`**: Set environment variables or create config file
- **`ImportError: No module named 'dynex'`**: Install package in development mode
- **`PermissionError: Cannot write to tmp/`**: Check directory permissions
- **`TimeoutError: Test exceeded time limit`**: Test is taking too long, check for infinite loops

### Getting Help

1. **Check test logs**: Look for detailed error messages
2. **Run individual tests**: Isolate the failing test
3. **Check dependencies**: Ensure all required packages are installed
4. **Verify configuration**: Make sure test environment is set up correctly

## Best Practices

### Test Organization

- Group related tests in classes
- Use descriptive test names
- Keep tests simple and focused
- Use fixtures for common setup

### Mocking Strategy

- Mock external dependencies
- Use realistic mock data
- Verify mock interactions
- Keep mocks simple

### Performance

- Use appropriate test markers
- Run fast tests frequently
- Use parallel execution when possible
- Monitor test execution time

### Maintenance

- Update tests when code changes
- Remove obsolete tests
- Keep test data current
- Document test requirements
