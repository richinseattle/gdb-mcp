#!/usr/bin/env python3
"""
Test runner for GDB MCP Server

This script runs the complete test suite and provides detailed reporting
on the functionality of all GDB MCP tools.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are available."""
    dependencies = {
        'gdb': 'GDB debugger',
        'gcc': 'GCC compiler (for test program compilation)',
        'python': 'Python interpreter'
    }
    
    available = {}
    for cmd, desc in dependencies.items():
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, timeout=5)
            available[cmd] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            available[cmd] = False
    
    return available


def run_tests(test_type='all'):
    """Run the test suite."""
    print("🧪 GDB MCP Server Test Suite")
    print("=" * 50)
    
    # Check dependencies
    print("\n📋 Checking Dependencies:")
    deps = check_dependencies()
    for cmd, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {cmd}: {'Available' if available else 'Not available'}")
    
    if not deps['python']:
        print("\n❌ Python is required but not available!")
        return False
    
    # Prepare pytest command
    pytest_cmd = ['python', '-m', 'pytest', '-v']
    
    if test_type == 'unit':
        pytest_cmd.extend(['tests/test-sessionManager.py', 'tests/test-gdbTools.py'])
        print("\n🔬 Running Unit Tests...")
    elif test_type == 'integration':
        pytest_cmd.extend(['tests/test-integration.py', 'tests/test-mcp-server.py'])
        print("\n🔗 Running Integration Tests...")
    else:
        # Run all test files explicitly
        pytest_cmd.extend([
            'tests/test-sessionManager.py', 
            'tests/test-gdbTools.py',
            'tests/test-integration.py', 
            'tests/test-mcp-server.py'
        ])
        print("\nRunning All Tests...")
    
    # Add coverage if available
    try:
        subprocess.run(['python', '-c', 'import coverage'], 
                      capture_output=True, check=True)
        pytest_cmd.extend(['--cov=modules', '--cov=server', '--cov-report=term-missing'])
        print("📊 Coverage reporting enabled")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  Coverage reporting not available (install coverage for detailed reports)")
    
    # Run tests
    print(f"\nExecuting: {' '.join(pytest_cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(pytest_cmd, cwd=Path(__file__).parent)
        success = result.returncode == 0
        
        print("-" * 50)
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return success
        
    except FileNotFoundError:
        print("❌ pytest not found! Please install it with: uv add pytest")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run GDB MCP Server tests')
    parser.add_argument('--type', choices=['all', 'unit', 'integration'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--check-deps', action='store_true',
                       help='Only check dependencies and exit')
    
    args = parser.parse_args()
    
    if args.check_deps:
        deps = check_dependencies()
        print("Dependency Status:")
        for cmd, available in deps.items():
            status = "✅" if available else "❌"
            print(f"  {status} {cmd}")
        return 0 if all(deps.values()) else 1
    
    success = run_tests(args.type)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())