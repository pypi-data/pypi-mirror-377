# AI Coding Agent Guidance: sys-design-diagram

Concise, project-specific context so an AI agent can contribute effectively. Keep responses grounded in these patterns.

## 1. Purpose & Big Picture

This project provides a Python CLI + Docker image to batch-generate system design diagrams from three sources:

- PlantUML (`*.puml`)
- Python `diagrams` library modules (`*.py` exposing `component_diagram(output_path: str)`)
- Mermaid (`*.mmd`)

Core orchestration lives in `ProcessDiagrams` (async fan-out per file). CLI (`sys-design-diagram`) exposes subcommands: `plantuml`, `diagrams`, `mermaid`, `process-all`.

## 2. Key Modules & Responsibilities

- `cli.py`: Argument/env resolution, default directory logic, delegates to `ProcessDiagrams.run`.
- `process_diagrams.py`: Async factory methods (`process_plantumls`, `process_diagrams`, `process_mermaids`,
  `process_all`). Builds task lists and gathers concurrently; resilient to per-file errors (logs and continues).
- `plantuml.py`, `mermaid.py`, `diagrams.py`: Implement `DiagramInterface.create()` for each diagram type.
  Subprocess execution for PlantUML & Mermaid; dynamic module load + function execution for `diagrams`.
- `utils.py`: Helper functions (module loading with defensive error wrapping, output path validation, PlantUML presence check).
- `log.py`: Central Loguru configuration (file + stdout). `configure_logging(verbose=True)` lowers level threshold.
- `exceptions.py` & `messages.py`: Domain-specific exception taxonomy + enumerated error message templates.

## 3. Execution & Control Flow (Example: `plantuml`)

1. CLI resolves `designs_dir` (CLI arg > `SDD_DESIGNS_DIR` > `./designs` > `/designs` container path)
   and `output_dir` (CLI arg > `SDD_OUTPUT_DIR` > `/output` > `./sys-design-diagram-output`).
2. Calls `ProcessDiagrams.run(ProcessDiagrams.process_plantumls, designs_dir, output_dir)`.
3. `process_plantumls` iterates each immediate subdirectory of `designs_dir`, finds `*.puml`, schedules async `PlantUMLDiagram.create()` tasks, gathers them concurrently.
4. Each `create()` spawns a subprocess (`plantuml -o <output_dir> <file>`), logs debug stdout/stderr, raises `PlantUMLExecutionError` on non-zero exit.

## 4. Conventions & Patterns

- Design root layout: `designs_dir/<design_name>/[files...]` — output mirrors this structure under `output_dir/<design_name>/`.
- Python `diagrams` modules MUST define `component_diagram(output_path: str)`; absence raises `DiagramsExecutionError` (tests enforce this).
- Async: All per-file generation uses `asyncio.create_subprocess_exec` or synchronous calls wrapped in async functions; concurrency aggregated via `asyncio.gather`.
- Error handling: Outer loops catch broad exceptions during directory iteration (logs once, continues). Individual task failures caught in `_run_task` (log only).
- Mermaid fallbacks: Browser / sandbox issues or missing CLI -> create plaintext placeholder `.png` (actually text) rather than failing hard.
- Logging: Always use provided `logger`; avoid configuring new handlers.
- Environment variable feature flags: `SDD_DESIGNS_DIR`, `SDD_OUTPUT_DIR`, `MERMAID_PUPPETEER_CONFIG`, `SDD_MERMAID_EXTRA_ARGS`.

## 5. Testing & Quality Gates

- Run tests: `hatch run test:all` (PyProject defines `all = ["test-cov"]`).
- Coverage: Enforced 100% (`[tool.coverage.report] fail_under = 100`). New code must include tests or adjust coverage config deliberately (avoid silent drops).
- Pytest options in `pyproject.toml` auto-generate HTML & XML reports into `tmp-output/` + HTML coverage into `htmlcov/`.
- Async tests use `pytest.mark.asyncio`.

## 6. Linting & Style

- Ruff configured for docstring checks only (`select = ["D"]`) + pydocstyle (google). Keep docstrings updated; missing/incorrect docstrings will fail lint.
- Line length = 120.
- Provide docstrings for new public functions/classes; prefer Google style.
- Mypy minimal (ignore-missing-imports); add types but don't introduce strictness changes casually.

## 7. Error & Message Strategy

- Always use `ErrorMessages` enum with `.value.format(...)` for raising domain errors to keep tests stable.
- Raise specific custom exceptions (e.g., `MermaidExecutionError`) — tests assert these types & message patterns.
- When adding new diagram types, create parallel exception classes + message constants.

## 8. Adding a New Diagram Type (Pattern Template)

1. Create `<name>.py` implementing `DiagramInterface` with async `create()` performing validation similar to existing ones.
2. Add processing method in `ProcessDiagrams` mirroring existing pattern (gather tasks, catch outer iteration exceptions).
3. Register CLI subcommand calling `_run(ProcessDiagrams.process_<name_plural>, ...)`.
4. Add tests: init validation, create success, create failure (execution), directory validation, integration via `process_all` if included.
5. Update README usage list and ensure coverage remains 100%.

## 9. Docker & Distribution

- Dockerfile installs system dependencies (PlantUML, Graphviz, Node, Chromium, fonts, Mermaid CLI). Local dev alternative: `Dockerfile_local`.
- PyPI release uses Hatch + VCS version; tagging triggers build & publish workflows.

## 10. Common Pitfalls & Gotchas

- Do NOT assume recursive search: only immediate child directories of `designs_dir` are scanned.
- `output_dir` sometimes resolved relative to `cwd`; ensure paths are absolute if changing path logic
  (see PlantUML vs Diagrams distinction—PlantUML & Mermaid conditionally rebuild absolute path when relative).
- Mermaid placeholders write text into `.png` path; consuming code/tests expect existence, not binary validity.
- Avoid blocking calls in new async code; use `asyncio` subprocess APIs.
- Changing log format or handler levels can break log-based expectations; use `configure_logging` only.

## 11. Quick Reference (Agent Use)

- Primary entrypoints: `ProcessDiagrams.*`, `PlantUMLDiagram.create`, `MermaidDiagram.create`, `DiagramsDiagram.create`.
- Directory resolution logic central: `_resolve_dirs` in `cli.py`.
- Module loading: `utils.load_module` (wraps importlib & normalizes errors).

## 12. When Unsure

Favor replicating existing patterns in analogous modules and extend tests to preserve 100% coverage.
Ask for clarification if a new feature changes directory layout or error semantics.

---
Provide improvements or new features with accompanying tests. Keep this file concise; trim any added verbosity.
