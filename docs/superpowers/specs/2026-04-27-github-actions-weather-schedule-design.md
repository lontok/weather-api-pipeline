# Daily Weather Pipeline on GitHub Actions

**Date:** 2026-04-27
**Status:** Approved

## Goal

Run `weather.py` once a day on GitHub Actions and commit the resulting `weather_data.csv` back to the repo, so `main` always reflects the most recent fetch.

## Triggers

- `schedule: cron "0 13 * * *"` — runs daily at 13:00 UTC (about 6am Pacific / 9am Eastern).
- `workflow_dispatch` — lets you click "Run workflow" in the Actions tab to trigger a run on demand. Useful for testing the workflow itself and for re-running after a failed day.

## Workflow Structure

One file: `.github/workflows/daily-weather.yml`. One job, `ubuntu-latest`, with these steps:

1. **Checkout** — `actions/checkout@v4` with `persist-credentials: true` so the same token can push the resulting commit.
2. **Set up Python** — `actions/setup-python@v5` with Python 3.12 and `cache: pip`.
3. **Install dependencies** — `pip install -r requirements.txt`.
4. **Run the pipeline** — `python weather.py`, with `WEATHER_API_KEY` injected from `secrets.WEATHER_API_KEY` as an environment variable.
5. **Commit the CSV if it changed** — configure the `github-actions[bot]` identity, then `git add weather_data.csv` and check `git diff --cached --quiet`. If there are staged changes, commit with a message like `chore: update weather_data.csv (2026-04-27)` and `git push`. If nothing changed, skip the commit.

## Code Changes to `weather.py`

Two small edits:

- Read the API key from the environment: `API_KEY = os.environ["WEATHER_API_KEY"]` (and `import os`). The `KeyError` if the variable is missing is intentional — fail fast rather than send unauthenticated requests.
- Uncomment `time.sleep(1)` so the 20-zip loop respects the rate limit on every run.

## New File: `requirements.txt`

```
requests
pandas
```

Pinning is unnecessary for a learning project; let CI install the latest compatible versions.

## Repo Setup (Manual, in GitHub UI)

These can't be done from code and need to happen before the first scheduled run:

- **Settings → Secrets and variables → Actions → New repository secret:** add `WEATHER_API_KEY` with a valid weatherapi.com key.
- **Settings → Actions → General → Workflow permissions:** select "Read and write permissions" so the workflow's `GITHUB_TOKEN` can push the CSV commit.

## Security Note

The current `API_KEY` value is hardcoded in `weather.py` and already exists in the public repo's git history. Rotate it on weatherapi.com after the new secret is in place. The old value should be considered compromised; rewriting git history to remove it is not worth the cost for a learning project, but the key itself must be invalidated.

## Out of Scope (YAGNI)

These were considered and explicitly cut:

- **Retries on API failure** — one bad day shows up in the next run.
- **External notifications (Slack, Discord, email beyond GitHub's default)** — GitHub already emails the repo owner on workflow failure.
- **Matrix builds, multiple Python versions, separate test job** — single script, single environment.
- **Dated snapshot files or appended time-series CSV** — the chosen output is "always overwrite `weather_data.csv` with the latest fetch."

## Success Criteria

- A new `.github/workflows/daily-weather.yml` runs successfully on `workflow_dispatch`.
- The job updates `weather_data.csv` on `main` with a fresh commit authored by `github-actions[bot]`.
- The next scheduled run at 13:00 UTC executes without manual intervention.
- A second consecutive run with no data change produces no empty commit.
