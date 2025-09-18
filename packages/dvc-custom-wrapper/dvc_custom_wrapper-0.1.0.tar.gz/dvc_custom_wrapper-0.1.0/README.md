# DVC MLOps Enhanced Commands Documentation

This project extends DVC with wrapper functions for experiment tracking, dataset management, metrics comparison, and tagging, making DVC more like Git for ML workflows.

---

## Key Enhancements Overview

- **Dual push history system:**
	- Internal log: `.dvc/push_history.json` (versioned, changes with checkout)
	- External/global log: configurable (default: `dvc_push_history_global.json` in project root), append-only, never changes with checkout
	- Logs are strictly separated: no syncing, deduplication, or cross-reading between them

- **Configurable global log path:**
	- The global log is now in the project directory (`dvc_push_history_global.json`) for better portability.

- **Universal `--internal` flag:**
	- All major commands (`logs`, `exp-list`, `dataset-list`, `metrics-diff`) accept `--internal` to switch between global and internal logs

- **Tag filtering and visibility:**
	- Use `--tag TAG [TAG ...]` with `dvc logs` to filter by one or more tags
	- When `--tag` is used, outputs only commit hashes and matching tag names (one per line), suppressing the table
	- Tags are always shown in log summaries


- **Strict log separation:**
	- Internal and external logs are never merged, deduplicated, or cross-read
	- Each log is updated independently on push

---

### 1. `dvc logs`
Show the history of DVC pushes, including commit info, artifacts, experiment name, metrics, and tags.

**Usage:**
```sh
dvc logs [-n N] [--dataset DATASET] [--show-all] [--internal] [--tag TAG [TAG ...]]
```
- `-n N`, `--number N`: Show the last N pushes (default: all)
- `--dataset DATASET`: Filter logs by dataset name
- `--show-all`: Show all available information (wider table)
- `--internal`: Show only the internal (repo) push history for the current commit/branch
- `--tag TAG [TAG ...]`: Filter logs by one or more tag names; outputs only commit hashes and tags (e.g., `commit_hash tag_name`)


> **Tip:** To filter experiments by tag, use `dvc logs --tag TAGNAME` to get commit hashes for that tag.

---

### 2. `dvc exp-list`
List all experiments and their metrics from push history.

**Usage:**
```sh
dvc exp-list [--internal]
```
- Lists experiments with metrics from the push history.
- Use `--internal` to show only the internal (repo) log.


---

### 3. `dvc tag`
Tag a specific commit in the push history.

**Usage:**
```sh
dvc tag <tag-name> <commit-hash>
```
- Example: `dvc tag v1.0 1234abc`
- Tags can be viewed in all `dvc logs` output and filtered with `--tag`.

---

### 4. `dvc metrics-diff`
Show the difference in metrics between two commits.

**Usage:**
```sh
dvc metrics-diff <commit1> <commit2> [--internal]
```
- Example: `dvc metrics-diff 1234abc 5678def`
- Shows the value of each metric in both commits.
- Use `--internal` to show only the internal (repo) log.
> **Tip:** To compare metrics for a specific tag, first run `dvc logs --tag TAGNAME` to get the commit hash, then use that hash in `dvc metrics-diff`.

---

### 5. `dvc dataset-list`
List all datasets tracked in the push history.

**Usage:**
```sh
dvc dataset-list [--internal]
```
- Lists all unique dataset names/paths found in the push history.
- Use `--internal` to show only the internal (repo) log.

---

## Example Workflow

```sh
# Add and track a dataset
dvc add data/sample.txt

# Commit and push as usual (your custom push logic will record extra info)
git add data/sample.txt.dvc .gitignore
git commit -m "Add sample dataset"
dvc push

# Tag a commit
dvc tag v1.0 <commit-hash>

# List experiments
dvc exp-list

# List datasets
dvc dataset-list

# Show metrics difference between two commits
dvc metrics-diff <commit1> <commit2>

# Show push logs with all details
dvc logs --show-all


# Filter logs by multiple tags
dvc logs --tag v1.0 v2.0
```

---

## Dependencies
- `rich`: For table display (optional, falls back to plain text)

Install with:
```sh
pip install rich
```

---

## Manual Global Log Path Configuration

The global log is now stored in the project directory as `dvc_push_history_global.json` for better portability. If you need to change it, edit the code in `dvc/repo/logs.py`.

---

## Notes
- Pushes are now recorded in two places:
	- `.dvc/push_history.json` (internal, versioned, changes with checkout)
	- `dvc_push_history_global.json` (global, in project root, append-only)
- By default, all commands use the global file for a complete history, but you can use `--internal` to see only the current repo state.
- All commands work on the push history and are designed for MLOps workflows.
- Internal and external logs are strictly separated and never merged or deduplicated.
- Ignored files (per `.dvcignore`) are filtered out from push history to avoid unwanted entries.

---

For help or issues, visit [https://dvc.org/support](https://dvc.org/support)
