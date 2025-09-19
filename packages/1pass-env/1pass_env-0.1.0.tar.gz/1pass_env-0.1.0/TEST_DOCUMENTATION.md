# Test Documentation for 1pass-env

## Overview

This document describes the comprehensive test suite for the 1pass-env tool, designed to achieve 95%+ code coverage and test all critical functionality.

## Test Structure

### Test Files

1. **`test_main.py`** - Main test suite covering core functionality
2. **`test_edge_cases.py`** - Edge cases and error scenarios
3. **`conftest.py`** - Shared fixtures and pytest configuration
4. **`run_tests.py`** - Test runner script
5. **`pytest.ini`** - Pytest configuration

### Test Categories

#### 1. Validation Functions (`TestValidationFunctions`)
- **`validate_fields()`** testing:
  - Valid field names
  - Empty/None field lists
  - Fields with spaces (invalid)
  - Empty field names
  - Overly long field names
- **`validate_output_path()`** testing:
  - Valid paths
  - Existing writable files
  - Directory creation
  - Non-writable directories
  - Non-writable files
  - Permission errors
  - Generic exceptions

#### 2. Authentication (`TestAuthentication`)
- **`get_client()`** testing:
  - Successful authentication
  - Missing service account token
  - Authentication failures
  - Network errors
  - Error propagation

#### 3. Import Functionality (`TestImportFunctionality`)
- Basic import operations
- File overwrite scenarios (confirm yes/no)
- Vault not found errors
- Item not found errors
- Field filtering
- Invalid field validation
- Missing authentication token
- Debug mode output
- Various item field attribute combinations
- File permission errors
- API errors (rate limiting, network issues)
- Empty vault scenarios
- No matching items

#### 4. Export Functionality (`TestExportFunctionality`)
- Basic export operations
- File not found errors
- Field filtering
- Missing fields warnings
- Empty .env files
- Vault creation errors
- File reading errors
- API permission errors

#### 5. Debug Mode (`TestDebugMode`)
- Debug output for import
- Debug output for export
- Traceback display on errors
- Field attribute inspection
- Progress logging

#### 6. Error Handling (`TestErrorHandling`)
- Client creation failures
- File permission errors
- Keyboard interrupt handling
- Fatal error scenarios
- Network timeouts
- API rate limiting

#### 7. CLI Integration (`TestCLIIntegration`)
- Help commands
- Default parameter values
- Command-line argument parsing
- Error message formatting

### Edge Cases Covered

#### Async Operations
- Proper async/await handling
- Exception propagation in async contexts
- Timeout scenarios

#### Field Attribute Variations
- Fields with only `id` attribute (no `title`/`label`)
- Fields with different attribute combinations
- Missing field attributes
- Various field types (CONCEALED, STRING, etc.)

#### File Operations
- Directory creation
- Permission errors
- Disk space issues
- Encoding errors
- Network drive issues

#### 1Password API Scenarios
- Empty vaults
- Missing items
- API rate limiting
- Network connectivity issues
- Authentication token expiration
- Permission denied scenarios

## Running Tests

### Quick Test Run
```bash
python run_tests.py
```

### Manual Test Execution
```bash
# Install dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Run all tests with coverage
pytest test_main.py test_edge_cases.py -v --cov=main --cov-report=html --cov-report=term-missing --cov-fail-under=95

# Run specific test categories
pytest test_main.py::TestValidationFunctions -v
pytest test_edge_cases.py::TestAsyncEdgeCases -v

# Run with specific markers
pytest -m "not slow" -v                    # Skip slow tests
pytest -m "unit" -v                        # Run only unit tests
pytest -m "integration" -v                 # Run only integration tests
```

### Coverage Reports

Tests generate multiple coverage reports:
- **Terminal**: Summary displayed after test run
- **HTML**: `htmlcov/index.html` - Interactive coverage report
- **XML**: `coverage.xml` - For CI/CD integration

## Test Coverage Goals

### Target: 95%+ Coverage

#### Covered Areas (100%)
- All validation functions
- Authentication flow
- CLI command parsing
- Error handling
- Debug output
- File operations
- 1Password API interactions

#### Partially Covered Areas
- Some edge cases in async error handling
- Platform-specific file permission scenarios

#### Excluded from Coverage
- Import statements
- `if __name__ == '__main__'` blocks
- Debug-only code paths
- Abstract method definitions

## Mock Strategy

### 1Password SDK Mocking
- **`AsyncMock`** for client operations
- **`Mock`** for data objects (vaults, items, fields)
- Realistic attribute simulation
- Error scenario simulation

### File System Mocking
- **`mock_open`** for file operations
- **`patch`** for path operations
- Permission error simulation
- Directory creation mocking

### Environment Mocking
- **`patch.dict`** for environment variables
- Token presence/absence scenarios
- Clean environment testing

## Test Data

### Sample Data Used
```python
# Sample vault
vault.id = 'test_vault_id_123'
vault.title = 'tokens'

# Sample item
item.id = 'item_id_123'
item.title = 'test-project'

# Sample fields
field.id = 'username'
field.title = 'API_KEY'
field.value = 'test_api_key_value'
field.type = 'CONCEALED'

# Sample .env content
API_KEY=test_api_key_123
SECRET_TOKEN=super_secret_token
DATABASE_URL=postgresql://localhost:5432/testdb
```

## Continuous Integration

### CI Configuration Example
```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    python run_tests.py
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Maintenance

### Adding New Tests
1. Add test methods to appropriate test class
2. Use descriptive test names (`test_function_scenario`)
3. Include docstrings explaining test purpose
4. Mock external dependencies
5. Assert both success and error conditions

### Best Practices
- One assertion per test (when possible)
- Clear test names indicating what is tested
- Comprehensive error scenario coverage
- Realistic mock data
- Independent test execution

## Performance Considerations

### Test Execution Time
- Unit tests: < 1 second each
- Integration tests: < 5 seconds each
- Full suite: < 30 seconds

### Memory Usage
- Minimal mock objects
- Cleanup after tests
- Temporary file management

## Debugging Tests

### Common Issues
1. **Mock not working**: Check import paths and patching locations
2. **Async tests failing**: Ensure proper `@pytest.mark.asyncio` usage
3. **Coverage gaps**: Run with `--cov-report=html` to identify uncovered lines
4. **File permission tests**: May behave differently on different platforms

### Debug Commands
```bash
# Run single test with verbose output
pytest test_main.py::TestValidationFunctions::test_validate_fields_valid -v -s

# Run with debug output
pytest --tb=long --capture=no

# Run with coverage and missing lines
pytest --cov=main --cov-report=term-missing
```