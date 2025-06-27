"""Pytest configuration and fixtures."""

import pytest
import os
import subprocess
import tempfile


@pytest.fixture(scope="session")
def gdb_available():
    """Check if GDB is available on the system."""
    try:
        result = subprocess.run(["gdb", "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture(scope="session")
def gcc_available():
    """Check if GCC is available on the system."""
    try:
        result = subprocess.run(["gcc", "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture
def test_program():
    """Create a temporary test program for debugging."""
    test_code = """
#include <stdio.h>
#include <stdlib.h>

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main(int argc, char *argv[]) {
    int number = 5;
    int result;
    
    printf("Calculating factorial of %d\\n", number);
    result = factorial(number);
    printf("Factorial of %d is %d\\n", number, result);
    
    return 0;
}
"""
    
    # Create temporary directory and files
    temp_dir = tempfile.mkdtemp()
    source_file = os.path.join(temp_dir, "test_program.c")
    binary_file = os.path.join(temp_dir, "test_program")
    
    # Write source code
    with open(source_file, 'w') as f:
        f.write(test_code)
    
    # Try to compile
    compiled = False
    try:
        subprocess.run([
            "gcc", "-g", "-o", binary_file, source_file
        ], check=True, capture_output=True)
        compiled = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    yield {
        'temp_dir': temp_dir,
        'source_file': source_file,
        'binary_file': binary_file,
        'compiled': compiled
    }
    
    # Cleanup
    try:
        if os.path.exists(source_file):
            os.remove(source_file)
        if os.path.exists(binary_file):
            os.remove(binary_file)
        os.rmdir(temp_dir)
    except:
        pass


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "requires_gdb: mark test as requiring GDB to be installed"
    )
    config.addinivalue_line(
        "markers", "requires_gcc: mark test as requiring GCC to be installed"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle conditional skipping."""
    # Check if GDB is available
    try:
        subprocess.run(["gdb", "--version"], 
                      capture_output=True, timeout=5, check=True)
        gdb_available = True
    except:
        gdb_available = False
    
    # Check if GCC is available
    try:
        subprocess.run(["gcc", "--version"], 
                      capture_output=True, timeout=5, check=True)
        gcc_available = True
    except:
        gcc_available = False
    
    # Skip tests based on availability
    skip_gdb = pytest.mark.skip(reason="GDB not available")
    skip_gcc = pytest.mark.skip(reason="GCC not available")
    
    for item in items:
        if "requires_gdb" in item.keywords and not gdb_available:
            item.add_marker(skip_gdb)
        if "requires_gcc" in item.keywords and not gcc_available:
            item.add_marker(skip_gcc)