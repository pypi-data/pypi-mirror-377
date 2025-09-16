# templafy Package Guidelines

## API Communication

- When communicating with APIs, use the `httpx` package unless explicitly instructed otherwise.
- When using HTTP status codes, use constants from the `httpx.codes` module instead of hardcoding them (e.g., `from httpx import codes`; `codes.OK`).

## Imports

- When importing internal modules, do not include the "src" folder in the import path as it is already defined in `pyproject.toml`.
- Example: `from templafy.auth import login` instead of `from src.templafy.auth import login`.

## Package API Guidelines

- Every package (mypkg/) must define a clear public API in its `__init__.py`.
- If submodules provide functionality that is likely to be directly consumed, re-export the relevant classes, functions, or constants in `__init__.py`.
- Use `__all__` to explicitly mark what is public.
- Internal utilities should remain private (prefix with `_` and do not re-export).
- This helps consumers of the package avoid deep imports like `mypkg.submodule.foo`.

## PeerTube API

- We are wrapping the Templafy API that adheres to the OpenAPI 3 standard.
- The JSON specification file can be found in `assets\openapi.json`.
- All API endpoints information is contained there.
- Note that the file might contain typos; do not correct them in the original JSON file, but correct them when using the text in the wrappers.

