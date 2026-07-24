# Spooled — Behavioral CI for AI Agents

[![PyPI](https://img.shields.io/pypi/v/spooled-ai)](https://pypi.org/project/spooled-ai/)

Catch behavioral drift in AI agents on every pull request. Fingerprint, diff, and gate against golden baselines.

## Quick start

```yaml
# .github/workflows/spooled.yml
name: Spooled Behavioral CI
on: [pull_request]

jobs:
  spooled:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: spooled-ai/spooled-action@v1
        with:
          baselines: .github/baselines
          test-command: pytest tests/agents/
```

That's it. The action will:

1. Install `spooled-ai` from PyPI (or an exact candidate source you pin)
2. Run your test command (which generates `.spooled/traces/*.jsonl`)
3. Compare each trace against the baseline using behavioral fingerprinting
4. Post a PR comment with the results
5. Fail the check if a policy violation is detected

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `baselines` | no | `.github/baselines` | Path to baseline directory or file |
| `test-command` | no | — | Command to generate traces (skip if traces exist) |
| `trace-dir` | no | `.spooled/traces` | Where to find traces |
| `policy` | no | — | Path to a `spooled-policy.yml` file. A configured path that does not exist fails the check. |
| `blocking` | no | `true` | Fail on incomplete analysis or a blocking behavioral decision |
| `license-key` | no | — | Spooled Pro license key. Without one, runs in community mode. |
| `post-comment` | no | `true` | Post or update a PR comment |
| `push-report` | no | `false` | Push CI report to your Spooled backend |
| `fetch-from-backend` | no | `false` | **Pro — Pattern 4.** Fetch production traces from backend instead of running tests in CI. Skips `test-command`. |
| `agent-id` | no | — | Agent ID to fetch traces for (used with `fetch-from-backend`) |
| `since` | no | `24h` | Time window for fetching traces — duration (`24h`, `7d`) or ISO timestamp |
| `commit-sha` | no | — | Filter fetched traces by git commit SHA prefix |
| `spooled-version` | no | — | Pin a specific `spooled-ai` version (e.g. `0.4.4`) |
| `spooled-source` | no | — | Install an exact SDK URL/path for prerelease testing; mutually exclusive with `spooled-version` |
| `setup-python` | no | `true` | Set up Python (disable if already configured) |
| `python-version` | no | `3.10` | Python version to install |
| `extra-deps` | no | — | Path to extra `requirements.txt` |

## Outputs

| Output | Description |
|---|---|
| `result` | `PASS` or `FAIL` |
| `total` | Total traces analyzed |
| `passed` | Traces matching baseline |
| `new-behavior` | Traces with new fingerprints |
| `policy-failures` | Traces with policy violations |
| `report-path` | Path to `ci-report/report.md` |
| `summary-path` | Path to `ci-report/summary.json` |

## Free vs Pro

| Feature | Free | Pro ($99/mo) |
|---|---|---|
| Action install + run | ✅ | ✅ |
| Full PR comment with diff | ✅ | ✅ |
| GitHub annotations | ✅ | ✅ |
| Merge blocking on policy violations | ✅ | ✅ |
| Local trace generation in CI (Pattern 1) | ✅ | ✅ |
| **Pattern 4** — fetch production traces from backend (no LLM calls in CI) | — | ✅ |
| Backend trace ingest from staging/production | — | ✅ |
| Hosted dashboard at app.spooled.ai | — | ✅ |
| Slack/webhook drift alerts | — | ✅ |
| 90-day history retention | — | ✅ |

**Free is fully featured for local-and-CI workflows.** The Pro upgrade unlocks production-trace-based comparison so you don't have to run LLMs in CI at all. Get a Pro license at [spooled.ai/pricing](https://spooled.ai/#pricing).

## How it works

Spooled records each tool call, LLM call, and HTTP request your agent makes. It hashes the structural shape of the run (tool sequences, decision counts, and output schemas) into a behavioral fingerprint.

On every PR, this action compares new fingerprints against committed baselines. By default it blocks unbaselined or unanalyzable traces, previously unseen consequential tools, and removal of always-observed tools or tool-schema keys. Use a versioned policy to gate exact tool scope, required action ordering, output contracts, or model changes.

Prompt, response, and tool-argument values are stripped at the SDK boundary. Only structural metadata—and configured argument key names—can contribute to a fingerprint. See the [privacy architecture](https://spooled.ai/docs/concepts/privacy-architecture) for details.

## Documentation

- [Quickstart](https://spooled.ai/docs/getting-started/quickstart)
- [Behavioral fingerprinting](https://spooled.ai/docs/concepts/behavioral-fingerprinting)
- [Policy engine](https://spooled.ai/docs/reference/policy-engine)
- [Privacy architecture](https://spooled.ai/docs/concepts/privacy-architecture)

## License

MIT
