# Claude AI Agent Instructions: sys-design-diagram

Project-specific guidance for Claude AI to contribute effectively to this system design diagram generation tool.

## Project Overview

**sys-design-diagram** is a Python CLI + Docker tool for batch-generating system design diagrams from:

- **PlantUML** (`*.puml`) - UML diagrams via Java PlantUML + Graphviz
- **Python diagrams** (`*.py`) - Code-as-diagrams using the `diagrams` library
- **Mermaid** (`*.mmd`) - Modern diagrams via Node.js mermaid-cli + Chromium

**Core Pattern**: Async fan-out processing per file type, with graceful error handling and container-first deployment.

## Architecture & Key Files

### CLI & Orchestration

- **`cli.py`**: Click-based CLI with environment variable fallbacks (`SDD_DESIGNS_DIR`, `SDD_OUTPUT_DIR`)
- **`process_diagrams.py`**: Core async orchestration. Methods: `process_plantumls()`, `process_diagrams()`, `process_mermaids()`, `process_all()`

### Diagram Generators (implement `DiagramInterface`)

- **`plantuml.py`**: Subprocess calls to `plantuml` command
- **`mermaid.py`**: Subprocess calls to `mmdc` (mermaid-cli) with Chrome fallback handling
- **`diagrams.py`**: Dynamic Python module loading, expects `component_diagram(output_path: str)` function

### Support Modules

- **`utils.py`**: Module loading, path validation, PlantUML detection
- **`log.py`**: Loguru configuration (file + stdout, verbose mode)
- **`exceptions.py`** + **`messages.py`**: Typed error handling with templated messages

## Directory Structure Convention

```text
designs_dir/
  design_name_1/
    *.puml, *.py, *.mmd files
  design_name_2/
    *.puml, *.py, *.mmd files

output_dir/
  design_name_1/
    generated diagrams (.png)
  design_name_2/
    generated diagrams (.png)
```

**Critical**: Only scans immediate subdirectories of `designs_dir` (NOT recursive).

## Development Workflows

### Testing

```bash
# Run all tests with coverage (requires 100%)
hatch run test:all

# Format code
hatch fmt
```

### Local Development

```bash
# Install in dev mode
pip install -e .

# Run CLI locally
sys-design-diagram process-all -d ./designs -o ./output
```

### Docker Usage

```bash
# Production image
docker run -v $(pwd)/designs:/designs -v $(pwd)/output:/output aydabd/sys-design-diagram:latest process-all

# Local development image
docker build -f Dockerfile_local -t sys-design-diagram-local .
```

## Code Patterns & Conventions

### Error Handling

- Use `ErrorMessages` enum for all user-facing errors: `ErrorMessages.FILE_NOT_FOUND.value.format(file_path=path)`
- Raise specific exceptions: `PlantUMLExecutionError`, `MermaidExecutionError`, `DiagramsExecutionError`
- Outer loops catch broad exceptions and log; individual tasks fail gracefully

### Async Patterns

- All diagram generation is async via `asyncio.create_subprocess_exec`
- Use `asyncio.gather(*tasks)` for concurrent processing
- Wrap sync operations in async functions when needed

### Logging

- Use the configured `logger` from `log.py`
- Debug level shows subprocess stdout/stderr
- Never configure additional handlers

### Mermaid Fallbacks

- Browser/sandbox failures → create text placeholder in `.png` file
- Missing `mmdc` command → create text placeholder
- Tests expect file existence, not binary validity

## Testing Strategy

### Test Structure

- **Fixtures**: `setup_design_dirs` creates temp directories with sample files
- **Async**: All diagram tests use `@pytest.mark.asyncio`
- **Mocking**: Subprocess calls mocked for reliability
- **Coverage**: 100% required (`fail_under = 100` in pyproject.toml)

### Test Files

- `test_cli.py`: CLI argument resolution, environment variables
- `test_*_diagrams.py`: Each diagram type (init, create, error cases)
- `test_process_diagrams.py`: Async orchestration and error resilience
- `test_utils.py`: Helper functions

## Adding New Features

### New Diagram Type

1. Create `new_type.py` implementing `DiagramInterface.create(output_dir: Path)`
2. Add `ProcessDiagrams.process_new_types()` method
3. Add CLI subcommand in `cli.py`
4. Create comprehensive test suite
5. Update this documentation

### Environment Variables

- `SDD_DESIGNS_DIR`: Override default designs directory
- `SDD_OUTPUT_DIR`: Override default output directory
- `MERMAID_PUPPETEER_CONFIG`: Puppeteer config file path
- `SDD_MERMAID_EXTRA_ARGS`: Additional mermaid-cli arguments

## Docker & Dependencies

### System Dependencies (in Docker)

- **PlantUML**: Java-based UML generation
- **Graphviz**: PlantUML rendering backend
- **Node.js + mermaid-cli**: Mermaid diagram generation
- **Chromium**: Headless browser for mermaid-cli
- **Fonts**: Comprehensive font packages for diagram rendering

### Python Dependencies

- **click**: CLI framework
- **diagrams**: Infrastructure-as-code diagrams
- **loguru**: Structured logging## Common Pitfalls

1. **Directory Scanning**: Only immediate subdirectories, not recursive
2. **Path Handling**: PlantUML/Mermaid handle relative paths differently than diagrams
3. **Mermaid Reliability**: Browser dependencies can fail; always provide fallbacks
4. **Coverage**: Must maintain 100% - add tests for any new code paths
5. **Async Context**: Don't mix blocking subprocess calls with async code

## Quick Commands Reference

```bash
# Development
hatch run test:all                    # Run tests
hatch fmt                            # Format code
hatch run dev:sys-design-diagram     # Run CLI in dev mode

# Production CLI
sys-design-diagram plantuml -d designs -o output
sys-design-diagram diagrams -d designs -o output
sys-design-diagram mermaid -d designs -o output
sys-design-diagram process-all -d designs -o output

# Docker
docker run -v $(pwd)/designs:/designs -v $(pwd)/output:/output aydabd/sys-design-diagram process-all
```

---

When contributing, focus on maintaining the async-first, error-resilient patterns while preserving 100% test coverage.
