# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing of the Jenbina project.

## Available Workflows

### 1. `run-tests.yml` - PR Testing
**Triggers:** Pull Request (opened, synchronize, reopened)
**Branches:** main, master, develop

This workflow automatically runs when:
- A new PR is created
- New commits are pushed to an existing PR
- A PR is reopened

**Features:**
- Runs tests on multiple Python versions (3.9, 3.10, 3.11)
- Generates test coverage reports
- Uploads coverage to Codecov
- Runs specific test suites (memory, chains, integration)

### 2. `test-suite.yml` - Manual & Push Testing
**Triggers:** 
- Push to main/master branch
- Manual workflow dispatch

**Features:**
- Manual trigger with test type selection
- Automatic testing on main branch pushes
- Selective test execution (all, memory, chains, integration)

## How to Use

### Automatic PR Testing
1. Create a pull request to main/master/develop
2. The `run-tests.yml` workflow will automatically trigger
3. Check the Actions tab to see test results
4. Coverage reports will be generated and uploaded

### Manual Testing
1. Go to the Actions tab in GitHub
2. Select "Test Suite" workflow
3. Click "Run workflow"
4. Choose the test type:
   - **all**: Run all test suites
   - **memory**: Run only memory-related tests
   - **chains**: Run only chain-related tests
   - **integration**: Run only integration tests
5. Click "Run workflow"

### Local Testing
Before pushing, you can run tests locally:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run all tests
cd tests
python -m pytest test_*.py -v

# Run specific test files
python test_memory.py
python test_chains.py
python run_chain_tests.py
```

## Test Coverage

The workflows generate coverage reports that show:
- Line coverage percentage
- Missing lines that need testing
- Coverage by file/module

Coverage reports are available in:
- GitHub Actions logs
- Codecov (if configured)
- Local pytest output

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Test Failures**: Check the specific test output in the Actions logs
3. **Coverage Issues**: Ensure test files are properly structured

### Debugging

To debug workflow issues:
1. Check the Actions tab for detailed logs
2. Look for specific error messages
3. Test locally to reproduce issues
4. Check Python version compatibility

## Configuration

### Environment Variables
The workflows use these environment variables:
- `PYTHON_VERSION`: Python version to use (set in matrix)
- `GITHUB_TOKEN`: Automatically provided by GitHub

### Dependencies
Required packages (installed automatically):
- All packages from `requirements.txt`
- `pytest` for test running
- `pytest-cov` for coverage reporting

## Contributing

When adding new tests:
1. Follow the existing test naming convention (`test_*.py`)
2. Place tests in the appropriate directory
3. Update this README if adding new test categories
4. Ensure tests work with the automated workflows
