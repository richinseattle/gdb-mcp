# Multi-Debugger MCP Server (LLDB and GDB)

A Model Context Protocol server that provides debugging functionality for both GDB and LLDB debuggers, for use with Claude Desktop, VSCode Copilot, or other AI assistants.

<p align="center">
  <img src="images/gdb-mcp.png" alt="GDB MCP Server" width="600">
</p>

## Quick Start

```bash
uv sync
uv venv
uv run server.py
```

## Integration

Note that you can use `uv run` to run the server.py script or you can use `uv venv` to create a virtual environment and then run `/home/youruser/dev/personal/GDB-MCP/.venv/bin/python /home/youruser/dev/personal/GDB-MCP/server.py`.

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gdb": {
      "command": "uv",
      "args": ["run", "/home/youruser/dev/personal/GDB-MCP/server.py"],
      "disabled": false
    }
  }
}
```

### VSCode Copilot

If you're using WSL:

```json
 "mcp": {
    "servers": {
      "my-mcp-server-4dc36648": {
        "type": "stdio",
        "command": "wsl",
        "args": [
          "/home/youruser/dev/personal/GDB-MCP/.venv/bin/python",
          "/home/youruser/dev/personal/GDB-MCP/server.py"
        ]
      }
    }
  }
```

If you're not using WSL:

```json
  "mcp": {
    "servers": {
      "my-mcp-server-db89eee1": {
        "type": "stdio",
        "command": "/home/youruser/dev/personal/GDB-MCP/.venv/bin/python",
        "args": ["/home/youruser/dev/personal/GDB-MCP/server.py"]
      }
    }
  }
```

## Experimental LLDB Support (macOS)

This project includes experimental native LLDB support alongside GDB, with automatic debugger selection.

<p align="center">
  <img src="images/lldb-mcp.png" alt="LLDB-MCP" width="600">
</p>

### Installation

To enable LLDB support on macOS, install LLVM (which includes LLDB) and python via Homebrew:

```bash
# Install LLDB for supporting python3.14 bindings
brew install llvm python3

# Install MCP and debugging dependencies
pip3 install mcp pygdbmi --break-system-packages
```

## Available Tools

### Unified Tools (Auto-detect debugger)
- `debugger_status()`: Show available debuggers and their status
- `debugger_start()`: Start debugging session with auto-detected debugger
- `debugger_terminate(session_id)`: Terminate debugging session
- `debugger_list_sessions()`: List all active debugging sessions
- `debugger_command(session_id, command)`: Execute debugger command

### LLDB-Specific Tools (Recommended for LLDB)
- `lldb_start()`: Start new LLDB debugging session
- `lldb_terminate(session_id)`: Terminate LLDB debugging session
- `lldb_list_sessions()`: List all active LLDB sessions
- `lldb_command(session_id, command)`: Execute arbitrary LLDB command

### GDB-Specific Tools

#### Session Management
- `gdb_start(gdb_path)`: Start new GDB debugging session
- `gdb_terminate(session_id)`: Terminate GDB debugging session
- `gdb_list_sessions()`: List all active GDB sessions

#### Program Control
- `gdb_load(session_id, program_path)`: Load executable into GDB
- `gdb_attach(session_id, pid)`: Attach GDB to running process
- `gdb_load_core(session_id, core_file)`: Load core dump file for analysis
- `gdb_continue(session_id)`: Continue program execution
- `gdb_step(session_id)`: Step into functions
- `gdb_next(session_id)`: Step over function calls
- `gdb_finish(session_id)`: Execute until current function returns

#### Breakpoints & Watchpoints
- `gdb_set_breakpoint(session_id, location)`: Set breakpoint at specified location
- `gdb_delete_breakpoint(session_id, number)`: Delete specific breakpoint
- `gdb_enable_breakpoint(session_id, number)`: Enable specific breakpoint
- `gdb_disable_breakpoint(session_id, number)`: Disable specific breakpoint
- `gdb_get_breakpoint_list(session_id)`: List all breakpoints with details
- `gdb_set_watchpoint(session_id, expression, type)`: Set watchpoint on variable/expression

#### Inspection & Analysis
- `gdb_backtrace(session_id)`: Show call stack/backtrace
- `gdb_print(session_id, expression)`: Print value of expression
- `gdb_examine(session_id, address, format)`: Examine memory at address
- `gdb_info_registers(session_id)`: Display processor registers
- `gdb_get_local_variables(session_id, print_values)`: Get local variables in current frame
- `gdb_get_function_arguments(session_id, print_values)`: Get function arguments for all frames
- `gdb_get_stack_frames(session_id, low_frame, high_frame)`: Get detailed stack frame information
- `gdb_evaluate_expression(session_id, expression)`: Evaluate expression with structured output

#### Memory & Disassembly
- `gdb_disassemble_function(session_id, function_name, mixed_mode)`: Disassemble function
- `gdb_disassemble_address_range(session_id, start_addr, end_addr, mixed_mode)`: Disassemble memory range
- `gdb_disassemble_around_pc(session_id, instruction_count, mixed_mode)`: Disassemble around program counter
- `gdb_read_memory_bytes(session_id, address, byte_count)`: Read raw memory bytes
- `gdb_examine(session_id, address, format_spec)`: Examine memory with format specification

#### Register Operations
- `gdb_get_register_names(session_id)`: Get list of all register names
- `gdb_get_register_values(session_id, register_numbers)`: Get register values
- `gdb_get_changed_registers(session_id)`: Get registers that changed since last stop

#### Thread Management
- `gdb_get_thread_info(session_id)`: Get information about all threads
- `gdb_switch_thread(session_id, thread_id)`: Switch to different thread

#### Symbol & Source Information
- `gdb_get_symbol_info(session_id, symbol_name)`: Get information about symbol
- `gdb_list_source_files(session_id)`: List all source files in program

#### General
- `gdb_command(session_id, command)`: Execute any arbitrary GDB command

## Usage Examples

### Running the Server

**With uv (recommended for development):**
```bash
uv run python server.py
```

**With system Python:**
```bash
python3 server.py
```

### MCP Configuration
```json
{
  "mcpServers": {
    "debugger-mcp": {
      "command": "python3",
      "args": ["/Users/ssmadi/dev/GDB-MCP/server.py"]
    }
  }
}
```

### Checking Status

You can verify debugger availability:
```python
from modules.lldb import LLDBSessionManager
from modules.gdb import GDBSessionManager
print("LLDB available:", LLDBSessionManager.is_available())
print("GDB available:", GDBSessionManager.is_available())
```

## Testing

```bash
uv run python run-tests.py --check-deps
uv run python run-tests.py --type all
```

## Examples

Check the `examples` directory for example prompts.

> Note: Example binaries are compiled to `arm64` and `amd64`, pick the one that matches your system architecture.

## License

This project is licensed under the GNU Version 3.0 License, see the LICENSE file for details.
