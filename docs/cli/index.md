# CLI Reference

`biohub-data-cli` is a command-line tool for downloading datasets published by CZ Biohub, including all data on the OPS Explorer. Given one or more collection IDs, it downloads the constituent files with progress bars and size estimates.

The CLI is published to [PyPI](https://pypi.org/project/biohub-data-cli/). Source lives in the [`chanzuckerberg/biohub-data-cli`](https://github.com/chanzuckerberg/biohub-data-cli) repository.

## Installation

Python 3.10+ is required.

```bash
pip install biohub-data-cli
```

This installs the `ops-data` command. To upgrade later:

```bash
pip install --upgrade biohub-data-cli
```

## Quick start

```bash
# See what a collection contains without downloading
ops-data download collection <collection-id> --dry-run

# Download a collection to the current directory
ops-data download collection <collection-id>

# Download multiple collections to a specific directory, skip the prompt
ops-data download collection <id-a> <id-b> -o ./data -y
```

Files land under `<outdir>/<collection-name>/<dataset-name>/`.

## Get help

The `--help` flag is available on every command and subcommand:

```bash
ops-data --help
ops-data download --help
ops-data download collection --help
```

## Commands

### `ops-data download collection IDs...`

Download one or more collections by ID.

| Option | Description |
| ------ | ----------- |
| `--dry-run` | Print per-dataset size statistics without downloading. Mutually exclusive with `-y`. |
| `-o, --outdir PATH` | Output directory. Defaults to `.` (current directory). |
| `-y, --yes` | Skip the size-estimate confirmation prompt. |

#### Dry run

`--dry-run` reports per-dataset byte totals before any data is downloaded. Files whose size cannot be determined in advance will surface as a warning in the summary.

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f --dry-run
```

#### Confirmation prompt

Before any bytes move, the CLI shows an aggregate size estimate and asks for confirmation. Pass `-y` / `--yes` to skip the prompt in scripts:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f -y
```

`--dry-run` and `-y` cannot be combined.

#### Failure handling

Per-URL failures are collected and reported at the end of the run. One bad URL will not abort an in-progress download — other files continue. The process exits non-zero if any download failed, so the exit code is safe to check in CI or shell scripts.

## Example Queries

The examples below use real collection IDs for the `leonetti` and `vesuvius` collections.

### Preview Size Before Downloading

To see exactly how large a download will be without transferring any bytes, use `--dry-run`:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f 019ce3fe-1353-7989-90a3-c080e231c848 --dry-run
```

This reports per-dataset size statistics for all listed collections in a single pass.

### Download a Single Collection

To download the `leonetti` collection to the current working directory:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f
```

You will be shown an aggregate size estimate and prompted to confirm. Typing `Y` will initiate the download. During the download, a progress bar is displayed.

### Download Multiple Collections

Pass collection IDs as space-separated positional arguments — there is no `--id` flag and no comma separator:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f 019ce3fe-1353-7989-90a3-c080e231c848
```

Each collection is resolved independently and written to its own subdirectory under the output path.

### Specify an Output Directory

Use `-o` / `--outdir` followed by a path to choose where files are written. For example, to download into a `data/` folder:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f -o ./data
```

Or, download multiple collections:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f 019ce3fe-1353-7989-90a3-c080e231c848 --outdir ~/Documents/ops-data
```

### Skip the Confirmation Prompt

For scripted or unattended use, pass `-y` / `--yes` to skip the size-estimate prompt:

```bash
ops-data download collection 196beb8f-ea3c-46f1-a46a-4ad6753a6e1f 019ce3fe-1353-7989-90a3-c080e231c848 -o ./data -y
```

## Tips

* Collection IDs are positional and space-separated — `ops-data download collection A B`, not `--id A --id B` or `A,B`.
* Run `--dry-run` first for large or unfamiliar collections to confirm the size before committing to a download.
* Use `--help` often: every subcommand supports it.
