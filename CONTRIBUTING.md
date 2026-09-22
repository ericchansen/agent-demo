# Contributing

## Getting Started

### Prerequisites

- Python 3.11+
- Azure CLI with Bicep (`az bicep install`)
- A Microsoft Fabric workspace (F2+ capacity)
- Access to a Fabric SQL analytics endpoint

### Setup

```bash
git clone <this-repo>
cd fabric-sales-agent-accelerator-scaffold
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # fill in your connection strings
```

## Development Workflow

1. **Branch** — create a feature branch from `main`: `feat/description`, `fix/description`, etc.
2. **Code** — make changes in `src/`, add tests in `tests/`.
3. **Test** — run `make lint`, `make format-check`, `make typecheck`, `make test`, and `make test-integration` before committing.
4. **Commit** — use conventional commit messages (see below).
5. **PR** — open a pull request against `main`.

## Code Style

We use **ruff** for linting and formatting, **mypy** for type checking.

| Setting      | Value |
|-------------|-------|
| Line length | 120   |
| Target      | py311 |
| Formatter   | ruff  |
| Type checker| mypy  |

```bash
make lint          # check for issues
make format        # auto-format
make format-check  # CI-friendly format check
make typecheck     # static type analysis
```

All code must pass `make lint`, `make format-check`, and `make typecheck` before merge.

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

**Types:**

| Type     | When to use                                |
|----------|--------------------------------------------|
| `feat`   | New feature or capability                  |
| `fix`    | Bug fix                                    |
| `docs`   | Documentation only                         |
| `infra`  | Bicep templates, CI/CD, deployment scripts |
| `test`   | Adding or updating tests                   |
| `chore`  | Dependency updates, config, tooling        |

**Scope** is optional but encouraged: `researcher`, `sharepoint`, `orchestrator`, `fabric`, `infra`.

Examples:
```
feat(researcher): add MCP tool for customer lookup
fix(orchestrator): handle empty agent response gracefully
infra: add Fabric capacity Bicep module
```

## Testing

```bash
make test              # unit tests (required to pass)
make test-integration  # local MCP stdio integration tests (required)
make test-eval         # LLM evaluation suite
```

- **Unit tests** (`tests/unit/`) — required for all PRs. Mock external services.
- **Integration tests** (`tests/integration/`) — start the real local MCP servers over stdio with mock research/SharePoint backends. They verify schemas, input rejection, protocol errors, recovery, and real DOCX/PPTX contents without tenant credentials. Required before merge.
- **Eval tests** (`tests/eval/`) — LLM output quality checks. Run manually for agent changes.

Place tests alongside the module they cover: `tests/unit/agents/test_researcher.py` for `src/agents/researcher/`.

### MCP SDK compatibility

The local servers target `mcp >= 2.2.0, < 3`. CI checks an exact MCP 2.2.0/jsonschema 4.20.0 environment and a separate fresh resolution within the declared ranges; these are tested configurations, not a claim that every future 2.x release is already verified. Use a fresh Python 3.11 environment for each configuration:

```bash
python -m pip install -e ".[dev]" "mcp==2.2.0" "jsonschema==4.20.0" "azure-ai-projects==2.7.0"
python -m pip check
python -m pip freeze
python -m ruff check .
python -m ruff format --check .
python -m mypy src/
python -m pytest tests/
```

Repeat in a second fresh environment with `python -m pip install -e ".[dev]"` and the same checks. Keep `requirements.txt` and `pyproject.toml` constraints aligned for shared dependencies. The SDK pins its own matching `mcp-types`; do not override it independently.

Azure AI Projects 2.7.0 is the selected, demonstrated working floor for this dependency set and is pinned in the minimum-dependency CI lane, not claimed to be the earliest compatible release. Its [package metadata](https://pypi.org/pypi/azure-ai-projects/2.7.0/json) requires `openai>=3.0.0`, and its OpenAI client implementation uses `httpx2`. The previous 2.2.0 floor failed to import with resolved OpenAI 3.16.1 because it imports `httpx`, which that dependency set no longer installs. This is a dependency-combination failure, not evidence that 2.2.0 lacks `server_label`. The project selects the verified current transport family instead of adding a second HTTP dependency solely to retain the older floor. Fabric tools use `server_label`, with real SDK serialization tests covering their connection IDs and unchanged approval setting.

[SDK 2 removed the low-level server's automatic JSON Schema validation](https://github.com/modelcontextprotocol/python-sdk/blob/v2.2.0/docs/migration.md#lowlevel-server-decorator-based-handlers-replaced-with-constructor-on_-params). Each callback uses the advertised schema before dispatch, without coercing inputs or inserting schema defaults. Keep permissive extra fields where the existing schema allows them; do not silently tighten schemas during an SDK upgrade.

Validation failures, unknown tool names, and known operational errors remain error-flagged tool results (`isError: true` on the wire). Unexpected programmer faults deliberately use the SDK 2 JSON-RPC error path instead of recreating SDK 1's blanket exception catch. Cancellation still propagates. Unknown protocol methods use SDK 2's `-32601` response; they are distinct from unknown tool names. Cover these boundaries in both unit and raw stdio tests.

Use `LATEST_HANDSHAKE_VERSION` when testing the newest `initialize` handshake: the SDK's newest overall protocol revision uses a different per-request envelope. Malformed JSON and invalid outer envelopes are rejected before tool dispatch and are not guaranteed a request-correlated response; test recovery with a subsequent valid request rather than waiting indefinitely for one.

## Infrastructure as Code

All Azure resources live in `infra/` as Bicep templates.

- **`main.bicep`** — top-level orchestration; references modules.
- **`modules/`** — one `.bicep` file per resource (e.g., `fabric-capacity.bicep`, `key-vault.bicep`).
- **`parameters/`** — environment-specific `.bicepparam` files (`dev.bicepparam`, `prod.bicepparam`).

Conventions:
- Use `camelCase` for parameter and variable names.
- Every module must accept `location` and `tags` parameters.
- Validate before committing: `make infra-validate`.

## Pull Requests

### Checklist

- [ ] `make lint` passes
- [ ] `make format-check` passes
- [ ] `make typecheck` passes
- [ ] `make test` passes
- [ ] `make test-integration` passes
- [ ] New/changed code has unit tests
- [ ] Bicep changes validated with `make infra-validate`
- [ ] PR description explains *what* and *why*

### Review Process

- All PRs require one approval before merge.
- Use **Rebase and merge** — keep history linear.
- Resolve all review comments before merging.
