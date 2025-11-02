# TODO: Remaining Fixes Needed

## Server.py Cleanup

- [ ] Replace all remaining `gdbTools.` references with `_get_gdb_tools().` pattern (50+ functions)
- [ ] Add try/catch error handling to all GDB tool functions
- [ ] Remove unused imports if any

## Test Suite Updates

- [ ] Update test imports from old module paths:
  - `from modules.sessionManager import GDBSessionManager` → `from modules.gdb import GDBSessionManager`
  - `from modules.gdbTools import GDBTools` → `from modules.gdb import GDBTools`
- [ ] Update tests to work with new DebuggerFactory pattern
- [ ] Add LLDB-specific tests
- [ ] Mock GDB for tests when not available
- [ ] Update integration tests for new server structure

## Current Status

**Working**: Server imports, LLDB functionality, unified tools
**Fixed**: sessionManager reference, critical gdbTools.execute_command
**Needs work**: Remaining gdbTools references, test suite

## Notes
- Server is functional for LLDB debugging
- GDB tools partially working (some functions still use old references)
- All new LLDB-specific tools working correctly
- Tests fail due to missing GDB and old import paths
