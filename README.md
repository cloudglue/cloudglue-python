# Cloudglue Python SDK

[![PyPI - Version](https://img.shields.io/pypi/v/cloudglue)](https://pypi.org/project/cloudglue)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.md)
[![Discord](https://img.shields.io/discord/1366541583272382536?logo=discord&label=Discord)](https://discord.gg/QD5KWFVner)

Cloudglue makes it easy to turn video into LLM ready data. Official Python SDK for the Cloudglue API.

## 📖 Resources

- [Cloudglue API Docs](https://docs.cloudglue.dev)
- [Terms of Service](https://cloudglue.dev/terms)
- [Privacy Policy](https://cloudglue.dev/privacy)
- [Pricing](https://cloudglue.dev/pricing)

> By using this SDK, you agree to the [Cloudglue Terms of Service](https://cloudglue.dev/terms) and acknowledge our [Privacy Policy](https://cloudglue.dev/privacy).


## Installation

You can install the Cloudglue Python SDK using pip:

```bash
pip install cloudglue
```

## Quick Start

```python
from cloudglue import Cloudglue

# Initialize the client
client = Cloudglue(api_key="your_api_key")  # Or use CLOUDGLUE_API_KEY env variable

# Define your messages
messages = [
    {"role": "user", "content": "What are aligned video captions?"}
]

# Make an API request
response = client.chat.completions.create(
    messages=messages,
    model="nimbus-001",
    collections=["abc123"], # Assumes collection already exists, otherwise create one first then reference here by collection id    
)

# Get the generated text
generated_text = response.choices[0].message.content
print(generated_text)
```

## Development

### Prerequisites

- Python 3.10+
- Make (for build tasks)
- Git

### Setup

Clone the repository and set up the development environment:

```bash
git clone https://github.com/cloudglue/cloudglue-python.git
cd cloudglue-python

brew install openapi-generator
make setup  # This will set up the virtual environment

# Initialize the API spec Git submodule
make submodule-init
```

### API Specification

The OpenAPI specification is maintained in a separate [repository](https://github.com/cloudglue/cloudglue-api-spec) and included as a Git submodule:

```bash
# Update the API spec to the latest version
make submodule-update

# After updating the spec, regenerate the SDK
make generate
```

### Building

```bash
make generate  # Generate SDK from OpenAPI spec
make build     # Build the package
```

### Releasing

Releases are published to PyPI automatically by the
[`Publish to PyPI`](.github/workflows/publish.yml) GitHub Actions workflow
whenever a `v*` tag is pushed. It uses
[OIDC trusted publishing](https://docs.pypi.org/trusted-publishers/) — no API
tokens are stored anywhere.

To cut a release:

```bash
# 1. Bump the version in pyproject.toml (e.g. 0.7.15 -> 0.7.16) and commit it.
# 2. Tag the commit. The tag MUST match the pyproject.toml version, prefixed
#    with "v" — the workflow fails fast if they differ.
git tag v0.7.16
git push origin v0.7.16
```

Pushing the tag triggers, in order:

1. **build** — verifies the tag matches `pyproject.toml`, builds the sdist +
   wheel, runs `twine check`.
2. **publish** — uploads the artifacts to PyPI via OIDC.
3. **github-release** — creates a [GitHub Release](https://github.com/cloudglue/cloudglue-python/releases)
   for the tag with auto-generated notes and the `.tar.gz` + `.whl` attached.

#### One-time setup

This is already configured for the `cloudglue` project, but for reference the
workflow depends on:

- A [PyPI trusted publisher](https://pypi.org/manage/project/cloudglue/settings/publishing/)
  for repo `cloudglue/cloudglue-python`, workflow `publish.yml`, environment `pypi`.
- A GitHub Environment named `pypi` (repo **Settings → Environments**).

#### Manual publishing (fallback)

The legacy token-based path still works if you need to publish outside CI. It
requires a [PyPI API token](https://pypi.org/manage/account/token/) scoped to the
`cloudglue` project, in `~/.pypirc` or via env vars:

```bash
make build
TWINE_USERNAME=__token__ TWINE_PASSWORD='pypi-...' make publish
```

### Project Structure

Project directory structure described below:

```
cloudglue/
├── __init__.py       # Main package initialization
├── client/           # Custom client wrapper code
│   └── main.py       # Cloudglue class implementation  
└── sdk/              # Auto-generated API code
dist/                 # Pre-built package dist
spec/                 # Git submodule with OpenAPI specification
└── spec/             # Nested spec directory
    └── openapi.json  # OpenAPI spec file
```

## Contact

* [Open an Issue](https://github.com/cloudglue/cloudglue-python/issues/new)
* [Email](mailto:support@cloudglue.dev)
