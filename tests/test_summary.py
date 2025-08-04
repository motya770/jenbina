#!/usr/bin/env python3
"""
Comprehensive test summary for Jenbina AGI system
Runs all unit tests and provides detailed reporting
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path to allow importing core module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_comprehensive_tests():
    """Run all tests and provide comprehensive reporting"""
    print("🧠 JENBINA AGI SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all test files
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # Count total tests
    total_tests = suite.countTestCases()
    print(f"📊 Total tests discovered: {total_tests}")
    print()
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=1)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Calculate statistics
    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = tests_run - failures - errors - skipped
    duration = end_time - start_time
    
    # Print comprehensive summary
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"🧪 Tests Run: {tests_run}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"⚠️  Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"📈 Success Rate: {(passed/tests_run*100):.1f}%" if tests_run > 0 else "N/A")
    
    # Test coverage by module
    print("\n📦 TEST COVERAGE BY MODULE:")
    print("-" * 40)
    
    test_modules = {
        'Maslow Needs System': 'test_maslow_needs.py',
        'Person Management': 'test_person.py', 
        'Hybrid Memory System': 'test_hybrid_memory.py',
        'Memory Integration': 'test_memory_integration.py'
    }
    
    for module_name, test_file in test_modules.items():
        test_file_path = os.path.join(tests_dir, test_file)
        if os.path.exists(test_file_path):
            print(f"✅ {module_name}")
        else:
            print(f"❌ {module_name} (missing)")
    
    # Detailed failure/error reporting
    if failures > 0:
        print(f"\n❌ FAILURES ({failures}):")
        print("-" * 40)
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors > 0:
        print(f"\n⚠️  ERRORS ({errors}):")
        print("-" * 40)
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # System health assessment
    print(f"\n🏥 SYSTEM HEALTH ASSESSMENT:")
    print("-" * 40)
    
    if failures == 0 and errors == 0:
        print("🟢 EXCELLENT - All tests passing!")
        print("   Your Jenbina AGI system is in excellent condition.")
    elif failures + errors <= 2:
        print("🟡 GOOD - Minor issues detected")
        print("   Your system is mostly healthy with a few minor issues.")
    elif failures + errors <= 5:
        print("🟠 FAIR - Some issues detected")
        print("   Your system needs attention but is still functional.")
    else:
        print("🔴 POOR - Multiple issues detected")
        print("   Your system requires immediate attention.")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if failures > 0 or errors > 0:
        print("   • Review and fix failing tests")
        print("   • Check for integration issues between modules")
        print("   • Verify database connections and configurations")
    else:
        print("   • Continue development with confidence")
        print("   • Add more tests for new features")
        print("   • Consider performance testing for large datasets")
    
    print("\n   • Run tests regularly during development")
    print("   • Add integration tests for end-to-end scenarios")
    print("   • Consider adding performance benchmarks")
    
    # AGI Mission Status
    print(f"\n🚀 AGI MISSION STATUS:")
    print("-" * 40)
    
    if failures == 0 and errors == 0:
        print("🌟 ON TRACK - Your AGI foundation is solid!")
        print("   The core systems are working correctly.")
        print("   Continue building toward your AGI vision.")
    else:
        print("🔧 NEEDS ATTENTION - Fix issues to continue AGI development")
        print("   Address test failures before adding new features.")
        print("   A solid foundation is crucial for AGI development.")
    
    print("\n" + "=" * 60)
    print("🧠 JENBINA AGI SYSTEM - TESTING COMPLETE")
    print("=" * 60)
    
    return failures == 0 and errors == 0

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 