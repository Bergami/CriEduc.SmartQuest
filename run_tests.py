#!/usr/bin/env python3
"""
SmartQuest Test Runner
Executes all tests in the SmartQuest project with proper configuration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"⚠️  Warnings/Errors:\n{result.stderr}")
        
        if result.returncode != 0:
            print(f"❌ Command failed with return code {result.returncode}")
            return False
        else:
            print(f"✅ {description} completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='SmartQuest Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', action='store_true', help='Skip slow tests')
    parser.add_argument('--no-cov', action='store_true', help='Skip coverage collection')
    
    args = parser.parse_args()
    
    # Set up environment
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 SmartQuest Test Runner")
    print(f"📁 Project Root: {project_root}")
    print(f"🐍 Python Version: {sys.version}")
    
    # Build pytest command
    base_command = ["python", "-m", "pytest"]
    
    # Add coverage if not disabled
    if not args.no_cov:
        base_command.extend([
            "--cov=app",
            "--cov-report=html:tests/coverage/html",
            "--cov-report=xml:tests/coverage/coverage.xml",
            "--cov-report=term-missing",
            "--cov-branch",
            "--cov-config=pyproject.toml"
        ])
    
    # Add verbosity
    if args.verbose:
        base_command.append("-v")
    else:
        base_command.append("-q")
    
    # Add test type filters
    if args.unit:
        base_command.extend(["-m", "unit"])
    elif args.integration:
        base_command.extend(["-m", "integration"])
    
    # Skip slow tests if requested
    if args.fast:
        base_command.extend(["-m", "not slow"])
    
    # Run tests
    success = True
    
    if args.unit:
        print("\n🧪 Running Unit Tests...")
        unit_command = base_command + ["tests/unit/"]
        success &= run_command(" ".join(unit_command), "Unit Tests")
        
    elif args.integration:
        print("\n🔗 Running Integration Tests...")
        integration_command = base_command + ["tests/integration/"]
        success &= run_command(" ".join(integration_command), "Integration Tests")
        
    else:
        print("\n🧪 Running All Tests...")
        all_command = base_command + ["tests/"]
        success &= run_command(" ".join(all_command), "All Tests")
    
    # Generate coverage report if requested
    if args.coverage and not args.no_cov:
        print("\n📊 Generating Coverage Report...")
        coverage_command = "python -m coverage html"
        run_command(coverage_command, "Coverage Report Generation")
        
        # Open coverage report
        coverage_file = project_root / "tests" / "coverage" / "html" / "index.html"
        if coverage_file.exists():
            print(f"📈 Coverage report generated: {coverage_file}")
    
    # Final summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests completed successfully!")
        print("🎉 SmartQuest test suite is healthy!")
    else:
        print("❌ Some tests failed!")
        print("🔧 Please check the output above for details.")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
