# Repository Guidelines

## Project Structure & Module Organization
- `src/`: C++ core and Python bindings (pybind11); OpenGL/GLES2 backends and platform code live here.
- `python/pixpy/`: Python package for the `pixpy` module, including the compiled `_pixpy*.so` and type stubs (`.pyi`).
- `pixide/`: Python IDE and utilities (editor, markdown, chat client, etc.).
- `tests/`: Pytest suite for Python components.
- `server/`: TypeScript WebSocket chat server with Jest tests.
- `docs/`, `examples/`, `external/`, `build/`: Documentation, sample code, third‑party sources, and CMake/Ninja build outputs.

## Build, Test, and Development Commands
- Build Python module: `make` (configures CMake + Ninja and builds `_pixpy` into `python/pixpy/`).
- Generate stubs: `make stubs` (runs `pybind11-stubgen` and fixes types).
- Package (wheel/sdist): `python -m build` (see `pyproject.toml`).
- Python tests: `make test` | verbose: `make test-verbose` | coverage: `make test-coverage`.
- Server (from `server/`): `npm run build` → `npm start` | tests: `npm test`.

## Coding Style & Naming Conventions
- Python: Black with line length 80; add type hints where practical (Pyright config provided). Modules and functions use `snake_case`; classes use `CamelCase`.
- C++: Respect `.clang-format` and `.clang-tidy`. Prefer consistent 2–4 space indents and self‑contained headers.
- Filenames: C++ `*.cpp`/`*.hpp`; tests `test_*.py` (see pytest config in `pyproject.toml`).

## Testing Guidelines
- Frameworks: Pytest for Python (`tests/`), Jest for `server/`.
- Conventions: Files `test_*.py`, classes `Test*`, functions `test_*`. Keep tests isolated and fast.
- Coverage: `make test-coverage` (HTML in `htmlcov/`). Aim to cover new code paths and error handling.

## Commit & Pull Request Guidelines
- Commits: Imperative, concise summaries (e.g., “Add voice recording”, “Fix editor scrolling”). Group related changes; avoid mixed concerns.
- PRs: Describe the change, rationale, and scope. Link issues, include screenshots for UI/behavior changes, list test coverage, and note any breaking changes or migrations.
- Pre‑submit: Run `make test`, ensure Black/clang‑format pass, and that no build artifacts are committed.

## Security & Configuration Tips
- Local runs often require `PYTHONPATH=python` when importing `pixpy` from the repo.
- Do not commit build outputs (`build/`, `dist/`, `*.so`, `stubs/`, `node_modules/`); `.gitignore` already covers these.
- Use Node 18+ for `server/` and Python 3.9+ for `pixpy`.

