<center>

# Python Project Template

[![PyPI version](https://img.shields.io/pypi/v/swebenchv2.svg)](https://pypi.org/project/swebenchv2/)
[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/CodingAgent/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/CodingAgent/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/CodingAgent/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/CodingAgent/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/CodingAgent/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/CodingAgent/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/CodingAgent.svg)](https://github.com/Mai0313/CodingAgent/graphs/contributors)

</center>

🚀 A production‑ready Python project template to help developers bootstrap new Python projects fast. It includes modern packaging, local tooling, Docker, and a complete CI/CD suite.

Click [Use this template](https://github.com/Mai0313/CodingAgent/generate) to start a new repository from this scaffold.

Other Languages: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ Highlights

- Modern `src/` layout and type‑hinted code
- Fast dependency management via `uv`
- Pre‑commit suite: ruff, mdformat(+plugins), codespell, nbstripout, mypy, uv hooks
- Strong typing: mypy with Pydantic plugin configuration
- Pytest with coverage and xdist; PR coverage summary comment
- Coverage gate at 80% with HTML/XML reports committed under `.github/`
- MkDocs Material with mkdocstrings (inheritance diagrams), markdown‑exec, MathJax
- Dev server at `0.0.0.0:9987`; bilingual docs scaffolded
- Docs generator script: by class/file, optional notebook execution, concurrency, preserves folder structure
- Async file processing via anyio and rich progress bars
- Packaging with `uv build` and changelog via `git-cliff`
- Automatic PEP 440 versioning from git via `dunamai` in CI
- Dockerfile multi‑stage with uv/uvx and Node.js; Compose services (Redis/Postgres/Mongo/MySQL) with healthchecks and volumes
- GitHub Actions: tests, quality, docs deploy, package build, docker image publish (GHCR with buildx cache), release drafter, auto labeler, secret scan, semantic PR, pre‑commit auto‑update
- Pre‑commit runs on multiple git stages (pre‑commit, post‑checkout, post‑merge, post‑rewrite)
- i18n‑friendly linting (Chinese punctuation allowed confusables)
- Alternative env managers documented (Rye, Conda)
- Legacy compatibility: export `requirements.txt` via `uv pip` if needed

## 🚀 Quick Start

Prerequisites:

- Python 3.10–3.13
- `uv` (install with `make uv-install`)
- Pre-commit hooks: either `uv tool install pre-commit` or `uv sync --group dev`

Local setup:

```bash
make uv-install               # once
uv sync                       # install base deps
uv tool install pre-commit    # or: uv sync --group dev
make format                   # run pre-commit hooks
make test                     # run tests
```

Run the example CLI:

```bash
uv run coding-agent
```

## 🧰 Commands Reference

```bash
# Development
make help               # List available make targets
make clean              # Clean caches, artifacts and generated docs
make format             # Run all pre-commit hooks
make test               # Run pytest across the repository
make gen-docs           # Generate docs from src/ and scripts/

# Git submodules (if you use them)
make submodule-init     # Init and update all submodules
make submodule-update   # Update all submodules to remote

# Dependencies (via uv)
make uv-install         # Install uv on your system
uv add <pkg>            # Add production dependency
uv add <pkg> --dev      # Add development dependency
# Sync optional groups
uv sync --group dev     # Install dev-only deps (pre-commit, poe, notebook)
uv sync --group test    # Install test-only deps
uv sync --group docs    # Install docs-only deps
```

## 📚 Documentation

- Live docs are built with MkDocs Material.
- Generate API docs locally and serve:

```bash
uv sync --group docs
make gen-docs
uv run mkdocs serve    # http://localhost:9987
```

- Auto generation script: `scripts/gen_docs.py` (supports .py and .ipynb)

```bash
# Generate docs by class (default)
uv run python ./scripts/gen_docs.py --source ./src --output ./docs/Reference gen_docs

# Generate docs by file
uv run python ./scripts/gen_docs.py --source ./src --output ./docs/Reference --mode file gen_docs
```

## 🐳 Docker and Local Services

`docker-compose.yaml` includes optional services for local development: `redis`, `postgresql`, `mongodb`, `mysql`, and an example `app` service that runs the CLI.

Create a `.env` file to configure ports and credentials (defaults shown):

```bash
REDIS_PORT=6379
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
MONGO_PORT=27017
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=mysql
MYSQL_USER=mysql
MYSQL_PASSWORD=mysql
MYSQL_PORT=3306
```

Run services:

```bash
docker compose up -d redis postgresql mongodb mysql

# Or run the example app container
docker compose up -d app
```

## 📦 Packaging and Distribution

Build artifacts with uv (wheel and sdist go to `dist/`):

```bash
uv build
```

Publish to PyPI (requires `UV_PUBLISH_TOKEN`):

```bash
UV_PUBLISH_TOKEN=... uv publish
```

CI builds also run automatically on tags matching `v*` and upload artifacts. Uncomment the publish step in `build_package.yml` to automate releases to PyPI.

### Run your CLI locally and from PyPI

- Local (from this repo):

```bash
uv run coding-agent
uv run cli
```

- From PyPI with `uvx` after publishing (ephemeral install):

```bash
# If your console script is named "coding-agent"
uvx coding-agent

# Disambiguate or pin a package/version
uvx --from your-package-name==0.1.0 your-entrypoint
```

## 🧭 Optional task runner (Poe the Poet)

Convenience tasks are defined under `[tool.poe.tasks]` in `pyproject.toml` and available after installing the dev group (`uv sync --group dev`) or via `uvx`:

```bash
uv run poe docs        # generate + serve docs (requires dev group)
uv run poe gen         # generate + deploy docs (gh-deploy) (requires dev group)
uv run poe main        # run CLI entry (same as uv run coding-agent)

# or ephemeral via uvx (no local install)
uvx poe docs
```

## 🔁 CI/CD Actions Overview

All workflows live in `.github/workflows/`. This section explains what each action does, when it runs, and what to configure.

- Tests (`test.yml`)

    - Trigger: Pull requests to `main` or `release/*` (ignores md files)
    - Runs pytest on Python 3.10/3.11/3.12/3.13 with coverage and comments a summary
    - Setup needed: none

- Code Quality Check (`code-quality-check.yml`)

    - Trigger: Pull requests
    - Runs ruff and other pre-commit hooks
    - Setup needed: none

- Docs Deploy (`deploy.yml`)

    - Trigger: Push to `main` and tags `v*`
    - Builds `mkdocs` site and publishes to GitHub Pages
    - Setup needed:
        - Enable GitHub Pages for the repo (Actions → Pages)
        - The workflow configures and uploads the site automatically

- Build Package (`build_package.yml`)

    - Trigger: Tags `v*`
    - Builds wheel/sdist via `uv build` and uploads artifacts; updates changelog
    - Optional publish: uncomment the `uv publish` step and add secret `UV_PUBLISH_TOKEN`

- Publish Docker Image (`build_image.yml`)

    - Trigger: Push to `main` and tags `v*`
    - Builds and pushes a Docker image to GHCR: `ghcr.io/<owner>/<repo>`
    - Setup needed: none (uses `GITHUB_TOKEN`); ensure `docker/Dockerfile` defines `prod` target

- Build Executable (`build_executable.yml`)

    - Trigger: Tags `v*` (Windows runner)
    - Currently stubs out packaging (example commented). Uploads a zip artifact
    - To ship a real executable, add your PyInstaller (or similar) steps

- Release Drafter (`release_drafter.yml`)

    - Trigger: Push to `main` and PR events
    - Maintains a draft release based on Conventional Commits

- Pull Request Labeler (`auto_labeler.yml`)

    - Trigger: PRs and pushes
    - Auto-applies labels defined in `.github/labeler.yml`

- Secret Scanning (`secret_scan.yml`)

    - Trigger: Push and PR
    - Runs gitleaks to detect leaked secrets

- Semantic Pull Request (`semantic-pull-request.yml`)

    - Trigger: PR open/edit/sync
    - Enforces Conventional Commit style PR titles

### CI/CD Configuration Checklist

- Conventional commits for PR titles (enforced by the workflow)
- Optional: set `UV_PUBLISH_TOKEN` secret to publish to PyPI
- Optional: enable GitHub Pages (used by docs deploy)
- Container Registry permissions are handled automatically via `GITHUB_TOKEN`

## 🧩 Example CLI

Console entry points are defined in `pyproject.toml` as `coding-agent` and `cli`. The example returns a simple `Response` model; replace with your own CLI logic.

```bash
uv run coding-agent
```

## 🤝 Contributing

- Open issues/PRs
- Follow the coding style (ruff, type hints)
- Use Conventional Commit messages and descriptive PR titles

## 📄 License

MIT — see `LICENSE`.
