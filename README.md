# Spooled — Behavioral CI for AI Agents

[![Marketplace](https://img.shields.io/badge/marketplace-spooled-purple)](https://github.com/marketplace/actions/spooled-behavioral-ci-for-ai-agents)

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
      - uses: spooled-ai/action@v1
        with:
          baselines: .github/baselines
          test-command: pytest tests/agents/
```

That's it. The action will:

1. Install `spooled-ai` from PyPI
2. Run your test command (which generates `.spooled/traces/*.jsonl`)
3. Compare each trace against the baseline using behavioral fingerprinting
4. Post a PR comment with the results
5. Fail the check if a policy violation is detected (Pro)

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `baselines` | yes | `.github/baselines` | Path to baseline directory or file |
| `test-command` | no | — | Command to generate traces (skip if traces exist) |
| `trace-dir` | no | `.spooled/traces` | Where to find traces |
| `policy` | no | — | Path to a `spooled-policy.yml` file |
| `blocking` | no | `true` | Fail the check on policy violations (Pro) |
| `license-key` | no | — | Spooled Pro license key. Without one, runs in community mode. |
| `post-comment` | no | `true` | Post or update a PR comment |
| `push-report` | no | `false` | Push CI report to your Spooled backend |
| `spooled-version` | no | — | Pin a specific `spooled-ai` version (e.g. `0.3.0`) |
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

Spooled records each tool call, LLM call, and HTTP request your agent makes. It hashes the structural shape of the run (tool sequences, decision counts, output schemas — never content) into a behavioral fingerprint.

On every PR, this action compares the new fingerprints against your committed baselines. If your agent's behavior changed — different tools, different sequences, different latency, different error patterns — you'll see it as a diff in the PR comment.

Content (prompts, responses, tool arguments) never leaves your infrastructure. The fingerprint is purely structural.

## Documentation

- [Quickstart](https://spooled.ai/docs/getting-started/quickstart)
- [Behavioral fingerprinting](https://spooled.ai/docs/concepts/behavioral-fingerprinting)
- [Policy engine](https://spooled.ai/docs/reference/policy-engine)
- [Privacy architecture](https://spooled.ai/docs/concepts/privacy-architecture)

## License

MIT
