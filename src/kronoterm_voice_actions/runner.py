import unittest
import os
import sys


def run_tests():
    # The current directory is /config, which is our package root.
    package_root = os.path.dirname(os.path.abspath(__file__))  # This will be /config

    # Add the package root to sys.path (already is, but good practice)
    sys.path.insert(0, package_root)

    # Discover all tests within the 'custom_components' directory
    loader = unittest.TestLoader()
    # Start discovering from the 'custom_components' directory within the current directory (/config)
    suite = loader.discover(
        start_dir=os.path.join(package_root, "custom_components"), pattern="test_*.py"
    )

    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the test suite
    result = runner.run(suite)

    # Return 0 if tests passed, 1 if any tests failed
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    exit(exit_code)
