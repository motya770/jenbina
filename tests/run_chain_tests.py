#!/usr/bin/env python3
"""
Test runner for Jenbina chain tests
Run this script to execute all chain-related unit tests
"""

import sys
import os
import unittest
import time

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_chain_tests():
    """Run all chain tests and return results"""
    
    # Discover and load all test modules
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test modules
    test_modules = [
        'test_chains',
        'test_chain_integration'
    ]
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            tests = test_loader.loadTestsFromModule(module)
            test_suite.addTests(tests)
            print(f"✅ Loaded {module_name}: {tests.countTestCases()} tests")
        except ImportError as e:
            print(f"❌ Failed to load {module_name}: {e}")
        except Exception as e:
            print(f"⚠️ Error loading {module_name}: {e}")
    
    # Run tests with detailed output
    print("\n" + "="*60)
    print("🧪 RUNNING JENBINA CHAIN TESTS")
    print("="*60)
    
    start_time = time.time()
    
    # Create test runner with detailed output
    test_runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Total tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Duration: {duration:.2f} seconds")
    
    if result.wasSuccessful():
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        
        # Print failure details
        if result.failures:
            print("\n🔴 FAILURES:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n🔴 ERRORS:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
        
        return False

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"🧪 Running specific test: {test_name}")
    
    # Import test modules
    from test_chains import TestChains, TestChainEdgeCases
    from test_chain_integration import TestChainIntegration, TestChainRealWorldScenarios
    
    # Create test suite with specific test
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Find and add the specific test
    test_classes = [TestChains, TestChainEdgeCases, TestChainIntegration, TestChainRealWorldScenarios]
    
    for test_class in test_classes:
        try:
            test_method = test_loader.loadTestsFromName(test_name, test_class)
            if test_method.countTestCases() > 0:
                test_suite.addTests(test_method)
                break
        except:
            continue
    
    if test_suite.countTestCases() == 0:
        print(f"❌ Test '{test_name}' not found")
        return False
    
    # Run the specific test
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Jenbina chain tests')
    parser.add_argument('--test', '-t', help='Run a specific test by name')
    parser.add_argument('--list', '-l', action='store_true', help='List all available tests')
    
    args = parser.parse_args()
    
    if args.list:
        # List all available tests
        print("📋 Available tests:")
        print("\nTestChains:")
        test_loader = unittest.TestLoader()
        tests = test_loader.loadTestsFromTestCase(unittest.TestCase)
        for test in test_loader.getTestCaseNames(unittest.TestCase):
            print(f"  - {test}")
        return
    
    if args.test:
        # Run specific test
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = run_chain_tests()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 