# Copilot Instructions

These are project-wide rules for GitHub Copilot (Chat + Completions).

## 🧰 Tooling (MANDATORY)
- **Use `uv` for all Python env + dependency tasks. Never use `pip`, `pipx`, or `poetry`.**
- Assume a local virtual environment at `./.venv`.
- Prefer **`pyproject.toml`** as the single source of truth for dependencies.
- When you need a package:
  - Prod dep: `uv add <package>`
  - Dev dep: `uv add --dev <package>`
- Install/sync deps from `pyproject.toml`: `uv sync`
- Run any command inside the env: `uv run <command>`

## 🐍 Virtualenv Policy
- If the venv **does not exist**, create it:
  - `uv venv` (creates `.venv` in the project)
  - Then `uv sync` to install deps.
- **Activation (only if explicitly needed by a script or instruction):**
  - macOS/Linux: `source .venv/bin/activate`
  - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Prefer `uv run <cmd>` over manual activation whenever possible.

## ✅ Linting & Style (flake8)
- All code must be **flake8-compliant**.
- Follow **PEP 8**, **type hints everywhere**, and clear docstrings.
- Keep functions focused and small; avoid unnecessary complexity.
- If adding lint tooling:
  - `uv add --dev flake8 flake8-bugbear flake8-comprehensions flake8-import-order`
- Example `.flake8` (create if missing):
[flake8]
max-line-length = 100
extend-ignore = E203,W503
select = C,E,F,W,B,B9
max-complexity = 10
import-order-style = google
- Before committing, run: `uv run flake8`

## 🐍 Pythonic Code
- Prefer composition over inheritance; keep modules cohesive.
- Use dataclasses for simple data; **use Pydantic models** for any validated I/O boundaries.
- Embrace modern Python:
- f-strings, `pathlib.Path`, `enum.Enum`, comprehensions
- `contextlib` for resource mgmt; `functools` for small utilities
- `typing` (`Literal`, `TypedDict`, `Annotated`, `Protocol`) where beneficial
- Write small, well-named functions. Avoid deep nesting.

## 🧱 Pydantic (v2) Guidelines
- Use **Pydantic** for config, request/response schemas, and validated domain objects.
- Prefer **v2** APIs:
- `from pydantic import BaseModel, ValidationError, field_validator, ConfigDict`
- Models should:
- Be fully typed.
- Validate and coerce inputs.
- Use `model_dump()` for serialization.
- Example:
```python
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    env: Literal["dev", "staging", "prod"]
    workers: int = 2
    log_level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"
    db_url: str
    timeout_s: Optional[float] = 10.0

    @field_validator("workers")
    @classmethod
    def _positive_workers(cls, v: int) -> int:
        if v < 1:
            raise ValueError("workers must be >= 1")
        return v
