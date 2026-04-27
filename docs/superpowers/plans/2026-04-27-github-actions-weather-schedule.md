# Daily Weather Pipeline on GitHub Actions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run `weather.py` once a day via GitHub Actions, committing the updated `weather_data.csv` back to `main`.

**Architecture:** A single workflow file (`.github/workflows/daily-weather.yml`) checks out the repo, installs Python deps, runs `weather.py` with the API key injected from a GitHub secret, and commits `weather_data.csv` back to `main` if it changed. The script itself is refactored to read its API key from `WEATHER_API_KEY` rather than the hardcoded value currently in source.

**Tech Stack:** Python 3.12, `requests`, `pandas`, GitHub Actions (`actions/checkout@v4`, `actions/setup-python@v5`).

**Spec:** `docs/superpowers/specs/2026-04-27-github-actions-weather-schedule-design.md`

---

## File Structure

- **Modify:** `weather.py` — read API key from env var, uncomment `time.sleep(1)`
- **Create:** `requirements.txt` — list runtime dependencies
- **Create:** `.github/workflows/daily-weather.yml` — the scheduled workflow
- **Manual (GitHub UI):** add `WEATHER_API_KEY` repo secret, set workflow permissions to "Read and write"
- **Manual (weatherapi.com):** rotate the old hardcoded key

`weather_data.csv` is unchanged by this work; it will be updated by CI runs.

---

## Task 1: Add requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Create the file**

```
requests
pandas
```

No version pinning — this is a learning project; let CI pick up compatible latest versions.

- [ ] **Step 2: Verify install works in the local venv**

Run:
```bash
source venv/bin/activate
pip install -r requirements.txt
```
Expected: pip reports `requests` and `pandas` as already satisfied (they were installed earlier) or installs them cleanly.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add requirements.txt for CI dependency install"
```

---

## Task 2: Refactor weather.py to read API key from environment

**Files:**
- Modify: `weather.py:1-5`

- [ ] **Step 1: Replace the hardcoded key with an environment read**

Change the top of `weather.py` from:

```python
import requests
import time
import pandas as pd

API_KEY = "<the-existing-hardcoded-key-value>"
```

to:

```python
import os
import requests
import time
import pandas as pd

API_KEY = os.environ["WEATHER_API_KEY"]
```

A missing env var raising `KeyError` is intentional — fail fast rather than send unauthenticated requests.

- [ ] **Step 2: Uncomment the rate-limit sleep**

In `weather.py`, find the line:

```python
    # time.sleep(1)
```

Change it to:

```python
    time.sleep(1)
```

- [ ] **Step 3: Verify the script fails fast without the env var**

Run:
```bash
source venv/bin/activate
unset WEATHER_API_KEY
python weather.py
```
Expected: `KeyError: 'WEATHER_API_KEY'` and no HTTP requests made.

- [ ] **Step 4: Verify the script succeeds with the env var set**

Run:
```bash
WEATHER_API_KEY="<paste-the-hardcoded-key-value-from-the-untracked-weather.py>" python weather.py
```
Expected: 20 city lines printed (one per second), the table prints, `weather_data.csv` is rewritten. Total runtime ~20s due to the new sleep.

(The hardcoded key is still valid until Task 6 rotates it.)

- [ ] **Step 5: Commit**

```bash
git add weather.py
git commit -m "refactor: read WEATHER_API_KEY from environment, enable rate-limit sleep"
```

---

## Task 3: Create the GitHub Actions workflow

**Files:**
- Create: `.github/workflows/daily-weather.yml`

- [ ] **Step 1: Create the workflow file**

```yaml
name: Daily weather pipeline

on:
  schedule:
    - cron: '0 13 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  fetch-weather:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run weather pipeline
        env:
          WEATHER_API_KEY: ${{ secrets.WEATHER_API_KEY }}
        run: python weather.py

      - name: Commit updated CSV if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add weather_data.csv
          if git diff --cached --quiet; then
            echo "No changes to weather_data.csv; skipping commit."
          else
            git commit -m "chore: update weather_data.csv ($(date -u +%Y-%m-%d))"
            git push
          fi
```

Notes on the YAML:
- `permissions: contents: write` at the workflow level grants the `GITHUB_TOKEN` push access, which is what the final commit step needs.
- The cron `0 13 * * *` fires once per day at 13:00 UTC.
- `cache: pip` uses `requirements.txt`'s hash as the cache key, so dependency installs become near-instant after the first run.
- The commit step's `git diff --cached --quiet` exits 0 when the staged tree matches HEAD; we only commit when it exits 1.

- [ ] **Step 2: Verify the YAML parses**

Run:
```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/daily-weather.yml'))"
```
Expected: no output, exit 0. (Any YAML error prints a parse message and exits non-zero.)

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/daily-weather.yml
git commit -m "ci: add daily weather pipeline workflow"
```

---

## Task 4: Push to GitHub and configure repo secret + permissions

**Files:** none (remote work).

- [ ] **Step 1: Push the new commits**

Run:
```bash
git push origin main
```
Expected: three new commits land on `origin/main`. The new workflow appears in the Actions tab but won't run until the secret is set (or until 13:00 UTC tomorrow).

- [ ] **Step 2: Add the WEATHER_API_KEY secret**

In GitHub UI:
1. Go to https://github.com/lontok/weather-api-pipeline/settings/secrets/actions
2. Click "New repository secret"
3. Name: `WEATHER_API_KEY`
4. Secret: paste a valid weatherapi.com key (the current hardcoded one works for now; Task 6 rotates it)
5. Click "Add secret"

Expected: the secret appears in the list as `WEATHER_API_KEY` with no value shown.

- [ ] **Step 3: Confirm workflow write permissions**

In GitHub UI:
1. Go to https://github.com/lontok/weather-api-pipeline/settings/actions
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Click "Save"

Expected: the radio for "Read and write permissions" is selected. (The workflow file also declares `permissions: contents: write`, but the repo-level setting is the ceiling, so this must allow it.)

---

## Task 5: Trigger a manual run and verify it works end-to-end

**Files:** none.

- [ ] **Step 1: Trigger the workflow via the Actions UI**

In GitHub UI:
1. Go to https://github.com/lontok/weather-api-pipeline/actions/workflows/daily-weather.yml
2. Click "Run workflow" → leave branch as `main` → click the green "Run workflow" button

Expected: a new run appears within ~10 seconds.

- [ ] **Step 2: Watch the run complete**

Wait for the run to finish (about 60–90 seconds — most of that is the 20× `time.sleep(1)` in the script).

Expected: the run completes with a green check. All five steps (Checkout, Set up Python, Install dependencies, Run weather pipeline, Commit updated CSV if changed) succeed.

- [ ] **Step 3: Verify the bot commit landed**

Run:
```bash
git pull origin main
git log -1 --pretty=format:'%an %s'
```
Expected: the most recent commit is authored by `github-actions[bot]` with a message like `chore: update weather_data.csv (2026-04-27)`.

- [ ] **Step 4: Verify the CSV is fresh**

Run:
```bash
head -3 weather_data.csv
```
Expected: header row plus two data rows. Temperatures should match what's plausible for the current time of day (sanity check, not exact match).

- [ ] **Step 5: Verify the no-op case (optional, validates the diff guard)**

Re-trigger the workflow immediately (Step 1 again). Wait for it to finish.

Expected: the run still succeeds, but the final step prints `No changes to weather_data.csv; skipping commit.` and no new commit appears on `main`. (If the temperatures changed between runs, a new commit *will* appear — that's also correct behavior.)

---

## Task 6: Rotate the leaked API key

**Files:** none (external service work).

The key on line 5 of the original `weather.py` is in public git history. Even though the working tree no longer references it, anyone reading the repo's history can pull it. Rotate it.

- [ ] **Step 1: Generate a new key on weatherapi.com**

1. Log in to https://www.weatherapi.com/my/
2. Either click "Reset" on the existing key, or generate a new one and delete the old.

- [ ] **Step 2: Update the GitHub secret**

In GitHub UI: Settings → Secrets and variables → Actions → click `WEATHER_API_KEY` → "Update secret" → paste the new value → click "Update secret".

- [ ] **Step 3: Re-trigger the workflow to confirm the new key works**

Same as Task 5, Step 1. Expect a green run.

- [ ] **Step 4: Confirm the old key is dead**

Run:
```bash
curl -s "https://api.weatherapi.com/v1/current.json?key=<the-old-key-value>&q=90045" | python -m json.tool
```
Expected: a JSON error response (e.g., `"error": {"code": 2006, "message": "API key is invalid."}`), confirming the old key is revoked.

---

## Done When

- `.github/workflows/daily-weather.yml` exists on `main`.
- A manual `workflow_dispatch` run completes green and produces a `github-actions[bot]` commit updating `weather_data.csv`.
- A second consecutive run with no data change produces no empty commit.
- The original hardcoded API key returns "invalid" against weatherapi.com.
- The next scheduled run at 13:00 UTC will execute without intervention.
