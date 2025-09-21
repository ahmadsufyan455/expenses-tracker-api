#!/usr/bin/env python3
"""
Test runner script for the expenses tracker application.
Provides different test execution options.
"""

import sys
import subprocess


def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return 1


def main():
    """Main test runner function"""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <option>")
        print("\nOptions:")
        print("  all           - Run all tests")
        print("  auth          - Run authentication tests")
        print("  budgets       - Run budget tests")
        print("  categories    - Run category tests")
        print("  transactions  - Run transaction tests")
        print("  user          - Run user tests")
        print("  coverage      - Run tests with coverage report")
        print("  verbose       - Run tests with verbose output")
        return 1

    option = sys.argv[1].lower()

    # Base pytest command
    base_cmd = "python -m pytest"

    # Command mapping
    commands = {
        "all": f"{base_cmd} tests/",
        "auth": f"{base_cmd} tests/test_auth_integration.py",
        "budgets": f"{base_cmd} tests/test_budgets_integration.py",
        "categories": f"{base_cmd} tests/test_categories_integration.py",
        "transactions": f"{base_cmd} tests/test_transactions_integration.py",
        "user": f"{base_cmd} tests/test_user_integration.py",
        "coverage": f"{base_cmd} tests/ --cov=app --cov-report=html --cov-report=term",
        "verbose": f"{base_cmd} tests/ -v -s"
    }

    if option not in commands:
        print(f"Unknown option: {option}")
        print("Run 'python run_tests.py' to see available options")
        return 1

    print(f"Running: {commands[option]}")
    return run_command(commands[option])


if __name__ == "__main__":
    sys.exit(main())
