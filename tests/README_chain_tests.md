# Jenbina Chain Tests

This directory contains comprehensive unit tests for all the chain functions in the Jenbina AGI system.

## 📁 Test Files

### `test_chains.py`
Comprehensive unit tests for individual chain functions:
- **Basic Needs Chain** - Tests the Maslow hierarchy needs analysis
- **World Description System** - Tests environment description generation
- **Action Decision Chain** - Tests decision-making based on needs and environment
- **Meta-Cognitive Action Chain** - Tests enhanced decision-making with self-reflection
- **Asimov Check System** - Tests compliance with Asimov's Laws
- **State Analysis System** - Tests state analysis and reflection
- **Maslow Decision Chain** - Tests Maslow-based decision making

### `test_chain_integration.py`
Integration tests for chain workflows and scenarios:
- **Full Simulation Workflow** - Tests complete simulation with all chains
- **Chain Data Flow** - Tests data passing between chains
- **Meta-Cognitive Integration** - Tests self-reflection integration
- **Error Recovery** - Tests graceful error handling
- **Performance Testing** - Tests chain performance under load
- **Real-World Scenarios** - Tests realistic use cases

### `run_chain_tests.py`
Test runner script with advanced features:
- Run all tests with detailed output
- Run specific tests by name
- List all available tests
- Performance timing and summary

## 🚀 Running Tests

### Run All Tests
```bash
cd tests
python run_chain_tests.py
```

### Run Specific Test
```bash
python run_chain_tests.py --test test_create_basic_needs_chain
```

### List All Tests
```bash
python run_chain_tests.py --list
```

### Run Individual Test Files
```bash
python test_chains.py
python test_chain_integration.py
```

## 🧪 Test Categories

### Unit Tests (`test_chains.py`)
- **Individual Chain Testing** - Each chain function tested in isolation
- **Mock LLM Testing** - Uses mocked LLM responses for fast, reliable testing
- **Error Handling** - Tests error conditions and edge cases
- **Performance Testing** - Tests response times and memory usage
- **Data Validation** - Tests input/output validation

### Integration Tests (`test_chain_integration.py`)
- **Workflow Testing** - Tests complete simulation workflows
- **Data Flow Testing** - Tests data passing between chains
- **Scenario Testing** - Tests realistic use cases
- **Load Testing** - Tests performance under multiple rapid calls
- **Memory Testing** - Tests memory usage patterns

## 📊 Test Coverage

The tests cover:

### ✅ Core Functionality
- [x] Basic needs analysis and decision making
- [x] World description generation
- [x] Action decision making
- [x] Asimov compliance checking
- [x] State analysis and reflection
- [x] Meta-cognitive processing

### ✅ Error Handling
- [x] Invalid LLM responses
- [x] Malformed JSON data
- [x] Missing parameters
- [x] Network failures (mocked)

### ✅ Performance
- [x] Response time testing
- [x] Memory usage monitoring
- [x] Load testing with multiple calls
- [x] Resource cleanup verification

### ✅ Integration
- [x] Chain-to-chain data flow
- [x] Complete simulation workflows
- [x] Real-world scenario testing
- [x] Meta-cognitive integration

## 🔧 Test Configuration

### Mock LLM Setup
Tests use a mocked LLM that returns predictable responses:
```python
self.mock_llm = Mock()
self.mock_llm.invoke.return_value.content = '{"response": "test response"}'
```

### Test Data
- **Person Object** - Real Person instance with MaslowNeedsSystem
- **World State** - Real WorldState instance
- **Meta-Cognitive System** - Real MetaCognitiveSystem instance

### Environment Setup
Tests automatically set up the Python path to import core modules:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## 📈 Test Results

### Expected Output
```
🧪 RUNNING JENBINA CHAIN TESTS
============================================================
✅ Loaded test_chains: 15 tests
✅ Loaded test_chain_integration: 12 tests

test_create_basic_needs_chain (test_chains.TestChains) ... ok
test_create_world_description_system (test_chains.TestChains) ... ok
test_create_action_decision_chain (test_chains.TestChains) ... ok
...

📊 TEST SUMMARY
============================================================
Total tests run: 27
Failures: 0
Errors: 0
Skipped: 0
Duration: 2.34 seconds
🎉 All tests passed!
```

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**
   - Ensure you're running from the `tests` directory
   - Check that core modules are in the correct location

2. **Mock LLM Issues**
   - Verify mock responses are properly formatted
   - Check that `invoke()` method is mocked correctly

3. **Test Data Issues**
   - Ensure Person and WorldState objects are properly initialized
   - Check that needs are set to expected values

### Debug Mode
Run tests with verbose output:
```bash
python -m unittest test_chains.TestChains.test_create_basic_needs_chain -v
```

## 🔄 Continuous Integration

These tests are designed to be run in CI/CD pipelines:

### GitHub Actions Example
```yaml
- name: Run Chain Tests
  run: |
    cd tests
    python run_chain_tests.py
```

### Pre-commit Hook
```bash
#!/bin/bash
cd tests && python run_chain_tests.py
```

## 📝 Adding New Tests

### For New Chain Functions
1. Add test method to `TestChains` class
2. Test both success and error cases
3. Verify input/output validation
4. Add performance testing if needed

### For New Integration Scenarios
1. Add test method to `TestChainIntegration` class
2. Test complete workflows
3. Verify data flow between chains
4. Test error recovery

### Test Naming Convention
- `test_function_name` - For individual function tests
- `test_scenario_name` - For integration scenario tests
- `test_error_condition` - For error handling tests

## 🎯 Test Goals

1. **Reliability** - Tests should be deterministic and repeatable
2. **Speed** - Tests should run quickly (under 10 seconds total)
3. **Coverage** - Tests should cover all major functionality
4. **Maintainability** - Tests should be easy to understand and modify
5. **Integration** - Tests should verify chain interactions work correctly

## 📚 Related Documentation

- [Core Module Documentation](../README.md)
- [Chain Function Documentation](../core/README.md)
- [API Reference](../docs/api.md) 