# Dynex SDK Testing Suite

This document provides a comprehensive guide to testing the Dynex SDK library.

## 🚀 Quick Start

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
python run_tests.py --all

# Or using make
make test
```

## 📁 Test Structure

```
dynex/
├── tests/                    # Test directory
│   ├── __init__.py          # Test package
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_config.py       # Configuration tests
│   ├── test_models.py       # Model class tests
│   ├── test_sampler.py      # Sampler tests
│   ├── test_api.py          # API tests
│   ├── test_integration.py  # Integration tests
│   ├── test_utils.py        # Utility function tests
│   ├── test_runner.py       # Custom test runner
│   ├── test_config.ini      # Test configuration file
│   └── README.md            # Detailed test documentation
├── quick_test.py            # Quick functionality test
├── run_tests.py             # Comprehensive test runner
├── pytest.ini              # Pytest configuration
├── requirements-dev.txt     # Development dependencies
├── Makefile                 # Make commands for testing
└── TESTING.md               # Detailed testing guide
```

## 🧪 Test Categories

### Unit Tests
- **Configuration**: `DynexConfig` class functionality
- **Models**: `BQM`, `SAT`, `CQM`, `DQM` model classes
- **Sampler**: `DynexSampler` class functionality
- **API**: `DynexAPI` class functionality
- **Utils**: Utility functions

### Integration Tests
- Complete workflows
- Component interactions
- End-to-end scenarios

### Configuration Tests
- Environment variable handling
- Configuration file loading
- Parameter validation

## 🛠️ Running Tests

### Basic Commands

```bash
# Quick functionality test
python quick_test.py

# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --coverage

# Run CI checks
python run_tests.py --ci

# Run full test suite with all checks
python run_tests.py --full
```

### Using Make

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage
make test-coverage

# Run linting
make lint

# Check code formatting
make format-check

# Run all CI checks
make ci-test

# Run everything
make test-all
```

### Using Pytest Directly

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestBQM::test_bqm_creation -v

# Run with coverage
pytest tests/ --cov=dynex --cov-report=html

# Run in parallel
pytest tests/ -n auto

# Run with specific markers
pytest tests/ -m "not slow"
```

## 🔧 Test Configuration

### Environment Variables

Tests automatically set these environment variables:

```bash
DYNEX_API_KEY=test_key_12345
DYNEX_API_SECRET=test_secret_67890
DYNEX_API_ENDPOINT=https://test-api.dynex.dev
DYNEX_FTP_HOSTNAME=test-ftp.dynex.dev
DYNEX_FTP_USERNAME=test_user
DYNEX_FTP_PASSWORD=test_password
```

### Test Fixtures

Available fixtures for testing:

- `test_config`: Pre-configured `DynexConfig`
- `mock_api`: Mocked `DynexAPI` for network-free testing
- `sample_bqm`: Sample `BinaryQuadraticModel`
- `sample_sat_clauses`: Sample SAT clauses
- `sample_cqm`: Sample `ConstrainedQuadraticModel`
- `sample_dqm`: Sample `DiscreteQuadraticModel`
- `temp_dir`: Temporary directory for file operations

### Mocking Strategy

Tests use extensive mocking to avoid external dependencies:

- **API calls**: Mocked using `unittest.mock.patch`
- **File operations**: Use temporary directories
- **Network requests**: Completely mocked
- **External services**: Mocked with realistic responses

## 📊 Coverage and Quality

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=dynex --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Code Quality

```bash
# Run linting
make lint

# Check formatting
make format-check

# Fix formatting
make format

# Run all quality checks
make ci-test
```

## 🚀 CI/CD Integration

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
# Run CI checks
python run_tests.py --ci

# Or using make
make ci-test
```

## 🐛 Debugging Tests

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

## 📝 Writing Tests

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

## 🎯 Test Examples

### Basic Functionality Test

```python
def test_bqm_creation(test_config, sample_bqm):
    """Test creating BQM model"""
    model = BQM(sample_bqm, config=test_config)
    
    assert model.type == 'wcnf'
    assert model.type_str == 'BQM'
    assert hasattr(model, 'clauses')
    assert hasattr(model, 'num_variables')
```

### Integration Test

```python
def test_bqm_workflow(test_config, sample_bqm):
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
        mock_internal.return_value.sample.return_value = mock_sampleset
        
        result = sampler.sample(num_reads=32, annealing_time=100)
        assert result == mock_sampleset
```

## 📈 Performance

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

## 🔍 Troubleshooting

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
   python quick_test.py
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

## 📚 Additional Resources

- **Detailed Testing Guide**: `TESTING.md`
- **Test Documentation**: `tests/README.md`
- **Migration Guide**: `MIGRATION_GUIDE.md`
- **GitHub Actions**: `.github/workflows/test.yml`
- **Makefile**: `Makefile`
- **Pytest Configuration**: `pytest.ini`

## 🤝 Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use appropriate fixtures
3. Add docstrings explaining what each test does
4. Include both positive and negative test cases
5. Mock external dependencies
6. Update documentation if adding new test categories

## 📞 Support

For help with testing:

1. Check the test logs for detailed error messages
2. Run individual tests to isolate issues
3. Verify all dependencies are installed
4. Check that the test environment is set up correctly
5. Review the troubleshooting section above
