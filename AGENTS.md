# AGENTS.md

## Cursor Cloud specific instructions

This repo is the Python SDK for the hosted CloudGlue API. There is no local backend to run — the SDK is a client library.

- Dependencies are installed automatically by the environment update script into a virtualenv at `.venv` (`python3 -m venv .venv` then `pip install -e .`). Use `.venv/bin/python` / `.venv/bin/pip`. Creating a venv requires the system `python3-venv` package, which is provided by the VM image (not the update script).
- The generated SDK in `cloudglue/sdk/` is **committed**, so `make generate` (which needs `openapi-generator` plus the `spec/` git submodule) and `make setup` are **not** required for day-to-day development. `pip install -e .` is sufficient.
- There is **no test suite** in this repo. A quick smoke check: `.venv/bin/python -c "from cloudglue import Cloudglue; Cloudglue(api_key='cg-x')"` instantiates the client and wires all resources against `https://api.cloudglue.dev/v1`.
- Real API calls require a valid `CLOUDGLUE_API_KEY` (keys start with `cg-`) and network access to `api.cloudglue.dev`.
- Other commands (`make build`, `make generate`, releasing) are documented in `README.md`, `CLAUDE.md`, and the `Makefile`.
