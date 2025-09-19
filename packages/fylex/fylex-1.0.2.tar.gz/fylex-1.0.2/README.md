# Fylex: The Linux File Ninja

[![PyPI](https://img.shields.io/pypi/v/fylex.svg)](https://pypi.org/project/fylex/)
[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/fylex?period=total\&units=INTERNATIONAL_SYSTEM\&left_color=black\&right_color=green\&left_text=downloads)](https://pepy.tech/projects/fylex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![20250918-2144-Tech-Neon-Design-simple-compose-01k5esk4tqf54rf0vh67m2ph4h.png](https://i.postimg.cc/L6F6V78T/20250918-2144-Tech-Neon-Design-simple-compose-01k5esk4tqf54rf0vh67m2ph4h.png)](https://postimg.cc/WtSvN5rF)

**Fylex** is a **production-ready, Linux-tailored file management tool** that combines the best of
`rsync`, `cp`, and Python’s `shutil` — but goes **beyond** with:

*  **Smart Copy & Move** with hashing (xxhash, blake3, SHA, MD5)
*  **Advanced conflict resolution** (rename, skip, replace, larger/smaller, newer/older, prompt)
*  **Filters**: regex, glob, exact filename matches, inclusion/exclusion
*  **Safety nets**: undo, redo, backup of deprecated files
*  **Data integrity**: hash verification, SQLite-backed hash cache for deduplication
*  **Metadata preservation**: permissions, timestamps, xattrs, ACLs (Linux-specific)
*  **CLI & Python API** for flexible usage


##
### Feature comparison  

| Feature / Tool                  | Fylex | cp (coreutils) | rsync | shutil (Python stdlib) |
|---------------------------------|-------|----------------|-------|-------------------------|
| Primary purpose                 | Smart local copy/move with safety nets | Basic copy | Fast sync (local/remote) | Library-level file ops |
| Undo / Redo                     | Yes — built-in JSON journaling | No | No | No |
| Hash verification               | Yes — xxhash, blake3, sha256, etc. | No | Partial — checksums optional | No |
| Hash cache (SQLite)             | Yes — avoids rehashing unchanged files | No | No | No |
| Duplicate detection (dest)      | Yes — size + hash | No | Partial — based on size/checksums | No |
| Conflict resolution             | Extensive — rename, replace, skip, newer/older, larger/smaller, prompt | None — overwrite only | Limited — flags like `--backup`, `--suffix` | None |
| Metadata preservation           | Yes — mtime, perms, xattrs, ACLs on Linux | Partial — `-a` preserves many | Partial — `-a` preserves many | Partial — `copystat` only |
| Atomic writes                   | Yes — via `fylex.tmp` | No | Partial — temp options exist | No |
| Logging / audit trail           | Yes — JSON logs per process | No | Partial — verbose logs only | No |
| CLI + Python API                | Yes — both | CLI only | CLI only (bindings exist) | Python API only |
| Delta transfer (network)        | No — local only | No | Yes | No |
| Remote / cloud support          | No — local-first | No | Yes — ssh/rsyncd | No |
| Cross-platform                  | Partial — Linux-first (xattrs/ACL best) | Yes | Yes | Yes |
| Performance (local)             | Very good — uses `copy_file_range` / `sendfile` | Good | Very good — efficient I/O | Moderate |
| Learning curve                  | Moderate — many options | Very low | Moderate to high — many options | Low |
| Best fit                        | Local integrity-critical workflows, reversible ops | Quick one-off copies | Local/remote sync and bandwidth-efficient backups | Small Python scripts |

---

## Honest strengths (where Fylex shines)

* **Undo / Redo** — Most competitors don’t offer a built-in reversible operation for arbitrary copy/move workflows. This is a major safety feature for power users.
* **JSON audit trail** — Every process writes machine-readable logs that enable reproducibility and automation (and fuel the undo/redo).
* **Hash verification + hash cache** — Optional verification plus an on-disk SQLite cache avoids repeated hashing of unchanged files and speeds repeated operations.
* **Flexible conflict resolution** — Many realistic conflict policies (rename with suffix, replace, choose larger/newer, prompt) are available out-of-the-box.
* **Linux metadata handling** — Attempts to preserve xattrs/ACLs when system tools are available—valuable for server or system admin workflows.
* **Atomic writes & backups** — Writes to a `.tmp` area and moves replaced files to `fylex.deprecated/PROCESS_ID` to avoid data loss during partial operations.
* **Good local performance** — Uses `copy_file_range` or `sendfile` and falls back sensibly for portability.

## Honest limitations (where other tools are better)

* **Not a network delta-sync tool** — If you need efficient remote sync over low bandwidth, `rsync` or `rclone` is better (rsync implements delta transfer).
* **Not a full backup system** — For encrypted, deduplicated backups with retention/versioning, choose `borg`/`restic`.
* **Linux-first** — Windows/macOS will work for basic operations, but xattr/ACL preservation and some system calls are Linux-specific; Fylex is intentionally optimized for Linux environments.
* **No built-in remote cloud backends** — If you need native S3/GoogleDrive/OneDrive support, `rclone` is the tool of choice.
* **Single-process / scale** — Current design favors correctness and simplicity; large-scale parallel distributed copying may require additional engineering (e.g., a distributed worker model).
* **Delta-copy library replacement** — You mentioned earlier replacing `pyrsync2` with a custom mechanism; Fylex does **not** implement network delta transfers (it focuses on local efficiency and correctness).

##




##  Safety Nets: Reliability First

Fylex is built with **data safety as priority**:

*  **Undo**: Rollback the last copy/move operation (removes created files, restores moved ones).
*  **Redo**: Replay an operation exactly as before.
*  **Backups**: Replaced/conflicting files are moved into `fylex.deprecated/` (per process).
*  **JSON logs**: Every operation is journaled (`json/{process_id}.json` + `.jsonl`).
*  **Verification**: Optional hash verification ensures copy integrity.
*  **Retries**: Up to 5 retries (`MAX_RETRIES`) on hash mismatch.
*  **Protections**: Prevents overwriting itself, copying into subdirectories, or backup loops.

##

## Installation

```bash
pip install fylex
```

Requires Python **3.8+**.
Linux recommended (for full xattr/ACL support).

##

##  Command Line Usage

### Copy files

```bash
fylex copy ~/Downloads ~/Backup --resolve rename --algo xxhash --verify --verbose
```

* Smartly copies, resolves conflicts by renaming, verifies integrity via hash.
* Deprecated/replaced files stored under `~/Backup/fylex.deprecated/PROCESS_ID/`.

### Move files

```bash
fylex move ./data ./archive --resolve newer --match-glob "*.csv"
```

* Moves only `.csv` files, replacing only if source is newer.

### Undo

```bash
fylex undo 1002
```

* Undoes process with ID `1002`.

### Redo

```bash
fylex redo 1002
```

* Replays process with ID `1002`.

##

##  Python API Usage

```python
from fylex import filecopy, filemove, undo, redo

# Copy with filters & conflict resolution
filecopy(
    src="~/Downloads",
    dest="~/Backup",
    resolve="rename",
    algo="xxhash",
    verify=True,
    match_glob="*.jpg",
    verbose=True
)

# Move and preserve metadata
filemove("project/", "archive/", resolve="newer", preserve_meta=True)

# Undo / Redo
undo("1002")
redo("1002")
```
##

##  Function Reference

### `filecopy(src, dest, ...)`

**Description:** Smartly copies files from `src` to `dest` with conflict handling, filters, and safety nets.

**Parameters:**

| Param             | Type        | Default    | Description                                                                                     |                                         |
| ----------------- | ----------- | ---------- | ----------------------------------------------------------------------------------------------- | --------------------------------------- |
| `src`             | `str`       | `Path`     | required                                                                                        | Source file or directory                |
| `dest`            | `str`       | `Path`     | required                                                                                        | Destination directory                   |
| `resolve`         | `str`       | `"rename"` | Conflict strategy: `rename`, `replace`, `skip`, `larger`, `smaller`, `newer`, `older`, `prompt` |                                         |
| `algo`            | `str`       | `"xxhash"` | Hash algo: `xxhash`, `blake3`, `md5`, `sha256`, `sha512`                                        |                                         |
| `chunk_size`      | `int`       | `16MB`     | Buffer size for reading files                                                                   |                                         |
| `verbose`         | `bool`      | `True`     | Log to stdout                                                                                   |                                         |
| `dry_run`         | `bool`      | `False`    | Simulate only                                                                                   |                                         |
| `summary`         | `str`       | `Path`     | `None`                                                                                          | Path to copy `fylex.log` summary        |
| `match_regex`     | `str`       | `None`     | Regex include filter                                                                            |                                         |
| `match_names`     | `list[str]` | `None`     | Exact names include filter                                                                      |                                         |
| `match_glob`      | `list[str]` | `None`     | Glob include filter                                                                             |                                         |
| `exclude_regex`   | `str`       | `None`     | Regex exclude filter                                                                            |                                         |
| `exclude_names`   | `list[str]` | `None`     | Exact names exclude filter                                                                      |                                         |
| `exclude_glob`    | `list[str]` | `None`     | Glob exclude filter                                                                             |                                         |
| `recursive_check` | `bool`      | `False`    | Dedup check recursively in `dest`                                                               |                                         |
| `verify`          | `bool`      | `False`    | Verify hashes after copy                                                                        |                                         |
| `has_extension`   | `bool`      | `False`    | Match file extension in dedup check                                                             |                                         |
| `no_create`       | `bool`      | `False`    | Do not create `dest` if missing                                                                 |                                         |
| `preserve_meta`   | `bool`      | `True`     | Preserve timestamps, permissions, xattrs, ACLs                                                  |                                         |
| `backup`          | `str`       | `Path`     | `"fylex.deprecated"`                                                                            | Folder for deprecated/conflicting files |
| `recurse`         | `bool`      | `False`    | Traverse subdirectories in `src`                                                                |                                         |

**Example:**

```python
filecopy("photos", "photos_backup", resolve="newer", match_glob="*.png", verify=True)
```

##

### `filemove(src, dest, ...)`

Same params as `filecopy`, but moves files instead.
If conflicts exist, originals are moved into backup.

##

### `undo(p_id, verbose=True, force=False)`

Rollback a process by ID.

| Param     | Type   | Description                             |
| --------- | ------ | --------------------------------------- |
| `p_id`    | `str`  | Process ID (JSON log ID)                |
| `verbose` | `bool` | Enable logs                             |
| `force`   | `bool` | Continue undo even if some entries fail |

##

### `redo(p_id, verbose=True, force=False)`

Replay a process by ID. Same parameters as `undo`.

##

##  Example Use Cases

* **Daily backup with safety nets**

  ```bash
  fylex copy ~/work ~/backup --resolve newer --verify --summary=backup.log
  ```

* **Selective move**

  ```bash
  fylex move ./data ./archive --match-regex ".*2025.*\.csv"
  ```

* **Quick rollback**

  ```bash
  fylex undo 1021
  ```

* **Replay last operation for reproducibility**

  ```bash
  fylex redo 1021
  ```

##

##  Internals

* Hash cache stored in `file_cache.db` (SQLite)
* JSON logs in `json/` (both `.jsonl` and `.json` formats)
* Temporary files in `dest/fylex.tmp/` for atomic writes
* Backups in `dest/fylex.deprecated/{process_id}/`

##

## License

MIT © 2025 Sivaprasad Murali

---

✨ With **Fylex**, file management on Linux is no longer just copying and moving — it’s **safe, verifiable, reversible, and smart**.

---

