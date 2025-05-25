import unittest
import os


def run_tests():
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Discover all tests in the current directory and subdirectories
    loader = unittest.TestLoader()
    suite = loader.discover(current_dir, pattern="test_*.py")

    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the test suite
    result = runner.run(suite)

    # Return 0 if tests passed, 1 if any tests failed
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    exit(exit_code)
