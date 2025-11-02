# TODO

## Test Suite Updates

- [ ] Update test imports from old module paths:
  - `from modules.sessionManager import GDBSessionManager` → `from modules.gdb import GDBSessionManager`
  - `from modules.gdbTools import GDBTools` → `from modules.gdb import GDBTools`
- [ ] Update tests to work with new DebuggerFactory pattern
- [ ] Add LLDB-specific tests
- [ ] Mock GDB for tests when not available
- [ ] Update integration tests for simplified server structure

## Notes

- Server is fully functional for both LLDB and GDB debugging
- Simplified approach: 4 GDB tools instead of 50+ (much cleaner!)
- All tools have proper error handling
- LLDB is primary debugger on macOS, GDB available via gdb_command()
- Tests need updating but server functionality is complete
