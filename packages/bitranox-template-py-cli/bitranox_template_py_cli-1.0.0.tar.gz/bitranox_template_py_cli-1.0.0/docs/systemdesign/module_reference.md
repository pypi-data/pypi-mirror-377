# Feature Documentation: bitranox_template_py_cli CLI

## Status
Complete

## Links & References
**Feature Requirements:** None (ad-hoc scaffold requirement)
**Task/Ticket:** None documented
**Related Files:**
- src/bitranox_template_py_cli/cli.py
- src/bitranox_template_py_cli/bitranox_template_py_cli.py
- src/bitranox_template_py_cli/__main__.py
- src/bitranox_template_py_cli/__init__conf__.py
- tests/test_basic.py

## Problem Statement
Provide a minimal but functional command-line interface (CLI) scaffold for the `bitranox_template_py_cli` package so developers can exercise the package, preview logging features, and validate the packaging scripts without additional wiring.

## Solution Overview
A Click-powered CLI entry point exposes three subcommands (`info`, `hello`, `fail`) behind a root group. Global options manage traceback verbosity via the shared `lib_cli_exit_tools` helper. The CLI wraps the library's stub functions, making it easy to test colored output, failure handling, and project metadata printing while reusing the shared exit tooling. Traceback preferences are scoped to each invocation, with the entrypoint restoring the prior setting once execution completes.

## Architecture Integration
**Where this fits in the overall app:**
Runs in the outer adapters layer as the package's main transport. It orchestrates user input into application/library functions (`hello_world`, `i_should_fail`, configuration printers) and routes exit behavior through `lib_cli_exit_tools`.

**Data flow:**
User invokes `bitranox_template_py_cli` CLI → Click parses args & stores global flags → Root command configures `lib_cli_exit_tools` → Subcommand executes library helper (`hello_world`, `i_should_fail`, or `__init__conf__.print_info`) → Results printed to stdout/stderr → `lib_cli_exit_tools.run_cli` returns exit code to caller.

## Core Components

### cli()
**Purpose:** Root Click group managing global options and shared context (traceback flag).
**Input:** Parsed CLI options (`--traceback`) and Click context.
**Output:** Configured context dict with traceback flag; side-effect of syncing `lib_cli_exit_tools.config.traceback`.
**Location:** src/bitranox_template_py_cli/cli.py

### cli_info()
**Purpose:** Display project metadata via `__init__conf__.print_info()`.
**Input:** None (uses global config set by `cli`).
**Output:** Formatted metadata printed to stdout.
**Location:** src/bitranox_template_py_cli/cli.py

### cli_hello()
**Purpose:** Demonstrate successful command path by invoking `hello_world()`.
**Input:** None.
**Output:** `Hello World` message to stdout.
**Location:** src/bitranox_template_py_cli/cli.py

### cli_fail()
**Purpose:** Exercise error handling by calling `i_should_fail()` which raises `RuntimeError`.
**Input:** None.
**Output:** Raises exception captured by Click/`lib_cli_exit_tools`; produces traceback when `--traceback` is active.
**Location:** src/bitranox_template_py_cli/cli.py

### main()
**Purpose:** Process wrapper that delegates to `lib_cli_exit_tools.run_cli` for consistent exit codes and signal handling while optionally restoring the prior traceback flag.
**Input:** Optional argv sequence plus keyword `restore_traceback` (default `True`), program name from `__init__conf__`.
**Output:** Integer exit code for the process; restores the pre-call traceback flag when requested.
**Location:** src/bitranox_template_py_cli/cli.py

### hello_world()
**Purpose:** Library helper returning the canonical greeting message for CLI reuse.
**Input:** None.
**Output:** Writes `Hello World` to stdout.
**Location:** src/bitranox_template_py_cli/bitranox_template_py_cli.py

### i_should_fail()
**Purpose:** Intentional failure hook to validate error paths and traceback emission.
**Input:** None.
**Output:** Raises `RuntimeError("I should fail")`.
**Location:** src/bitranox_template_py_cli/bitranox_template_py_cli.py

## Implementation Details
**Dependencies:**
- External: `click` for CLI parsing, `lib_cli_exit_tools` for standardized exit handling.
- Internal: `bitranox_template_py_cli.bitranox_template_py_cli` helpers, project metadata in `__init__conf__`.

**Key Configuration:**
- Global `--traceback/--no-traceback` flag toggles full traceback printing through `lib_cli_exit_tools.config.traceback`. The CLI restores the prior configuration on completion, while the module `__main__` entry point defers restoration until after exception reporting.
- Program metadata (`shell_command`, `version`, `title`) loaded from `__init__conf__`.

**Database Changes:**
None.

## Testing Approach
**How to test this feature:**
- Run `pytest tests/test_basic.py::test_cli_hello_and_fail_commands` for command behavior.
- Use `pytest tests/test_basic.py::test_module_main_traceback` to confirm traceback toggling.
- Manual smoke test: `python -m bitranox_template_py_cli --traceback fail` and `bitranox_template_py_cli hello` after editable install.

**Automated tests to write:**
Existing tests cover greeting output, traceback propagation, and `main` delegation.

**Edge cases to verify:**
- Invoking `fail` without `--traceback` should still exit non-zero with truncated stack per `lib_cli_exit_tools` defaults.
- Ensure `--traceback` flag persists for nested commands when new subcommands are added.
- Confirm metadata printing remains consistent after version bumps.

**Test data needed:**
No external data; CLI tests rely on Click's `CliRunner`.

## Known Issues & Future Improvements
**Current limitations:**
- Only exposes stub functionality.
- Traceback restoration depends on callers that disable `restore_traceback` resetting the flag when they finish (the default handles this automatically).

**Edge cases to handle:**
- Future commands should respect the traceback flag and return structured errors.
- Need graceful handling for unexpected exceptions once richer features exist.

**Planned improvements:**
- Replace `print`-based helpers with structured logging adapters when available.
- Introduce configuration-driven command registration.

## Risks & Considerations
**Technical risks:**
- Callers that opt out of automatic traceback restoration (`restore_traceback=False`) must ensure they reset the flag after error handling.
- Adding dependencies without wrapping them as adapters could violate Clean Architecture boundaries.

**User impact:**
- Failing command intentionally exits non-zero; document clearly to avoid confusion.
- Traceback defaults to hidden; users may need to pass `--traceback` to debug issues.

## Documentation & Resources
**Related documentation:**
- README.md (usage overview)
- CONTRIBUTING.md (development workflow)

**External references:**
- Click documentation for command extensions
- lib_cli_exit_tools project docs (shared tooling)

---
**Created:** 2025-09-17 by GPT-5 Codex  
**Last Updated:** 2025-09-17 by GPT-5 Codex  
**Review Date:** 2025-12-17
