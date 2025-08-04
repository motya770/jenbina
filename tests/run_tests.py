#!/usr/bin/env python3
"""
Test runner for all Jenbina unit tests
Runs all test modules and provides a summary
"""

import unittest
import sys
import os
import time

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

def run_all_tests():
    """Run all test modules"""
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all test files
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    # Return success/failure
    return len(result.failures) == 0 and len(result.errors) == 0

def run_specific_test(test_module):
    """Run a specific test module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print(f"\nTest module '{test_module}' completed in {end_time - start_time:.2f} seconds")
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1]
        success = run_specific_test(test_module)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1) 