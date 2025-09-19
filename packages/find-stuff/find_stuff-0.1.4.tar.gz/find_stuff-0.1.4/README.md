# find-stuff

Lightweight code search for your own projects.

The library scans your folders for Git repositories, indexes the files you
choose (by extension), and lets you search quickly from the terminal or from
Python. It uses a simple SQLite database with an inverted index built from
tokens found in your files. The CLI is friendly, the internals are small and
typed, and everything runs locally.

## What it is good for

- Fast grep-like queries across many repos without opening an editor
- Exact or regex term matching, case-sensitive or not
- “All terms” vs “Any term” logic
- Limiting results and filtering by file extensions at search time

## Install

The steps below are written for beginners. They show how to:

1) Install Python
2) Create a private “virtual environment”
3) Get the project from GitHub
4) Install it into your environment and run it

You only need to do this once on your computer. After that, you can just
activate the environment and use the tool.

### 1) Install Python (version 3.11 or newer)

- Windows:
  - Go to the official Python website: `https://www.python.org/downloads/`
  - Download “Python 3.x” for Windows and run the installer.
  - Important: On the first screen, check the box “Add Python to PATH”,
    then click Install.
  - After install, open PowerShell and type:

    ```powershell
    python --version
    ```

    You should see something like `Python 3.11.8` (any 3.11+ is fine).

- macOS:
  - Visit `https://www.python.org/downloads/` and install the latest 3.x for macOS.
  - Open Terminal and type `python3 --version` to confirm.

- Linux (Ubuntu/Debian):
  - Open Terminal and run:

  ```bash
  sudo apt update && sudo apt install -y python3 python3-venv python3-pip
  ```

  - Confirm with: `python3 --version`

### 2) Create a virtual environment (keeps things clean)

Pick a folder where you want to keep this project (for example,
`D:\tools\find-stuff` on Windows or `~/tools/find-stuff` on macOS/Linux). Then:

- Windows PowerShell:

  ```powershell
  python -m venv .venv
  . .venv\Scripts\Activate.ps1
  ```

- macOS/Linux Terminal:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

If activation worked, your prompt will show `(.venv)` at the start. While this
is active, anything you install stays private to this folder.

### 3) Get the project from GitHub

If you have Git installed, you can clone the repository. If not, you can click
the green “Code” button on GitHub and download the ZIP, then unzip it into your
chosen folder.

Using Git (recommended):

```bash
git clone https://github.com/pyl1b/find-stuff.git
cd find-stuff
```

### 4) Install the tool into your environment

With the virtual environment still active and inside the `find-stuff` folder,
run:

- Windows PowerShell:

  ```powershell
  python -m pip install --upgrade pip
  python -m pip install -e .
  ```

- macOS/Linux:

  ```bash
  python3 -m pip install --upgrade pip
  python3 -m pip install -e .
  ```

This installs the library and the `find-stuff` command.

### 5) Try it out

Show the help to confirm it’s installed:

```bash
find-stuff --help
```

Later, when you come back to use the tool again, just re-activate the environment (step 2) and you’re ready.

## TL;DR

- Build the index under a root folder, choosing the extensions you care about:

```bash
find-stuff rebuild-index D:\code --db D:\code\.find_stuff\index.sqlite3 --ext py --ext md
```

- Search it:

```bash
find-stuff search --db D:\code\.find_stuff\index.sqlite3 foo bar
```

---

## CLI

All commands share logging flags: `--debug/--no-debug`, `--trace/--no-trace`,
and `--log-file` to redirect logs. Version is available via `--version`.

### rebuild-index

Recreate the database from scratch by scanning for Git repositories under a
root and indexing tracked files of the given extensions.

```bash
# Index only Python files under the root directory
find-stuff rebuild-index D:\projects --ext py

# Index multiple extensions, writing DB to a custom path
find-stuff rebuild-index D:\work --db D:\work\.find_stuff\index.sqlite3 --ext py --ext md --ext txt
```

### add-to-index

Append newly found repositories and files without wiping existing data.

```bash
# Add new repos under the same root into an existing DB
find-stuff add-to-index D:\work --db D:\work\.find_stuff\index.sqlite3 --ext py
```

### search

Query the index for files containing terms. By default, a result must contain
all terms. Use `--any` to match if any term is present. Use `--regex` to
interpret terms as regular expressions. `--case-sensitive` controls case
sensitivity. Use `--limit` to cap results and `--ext` to filter by extension at
search time.

```bash
# Require all terms (default)
find-stuff search --db D:\work\.find_stuff\index.sqlite3 foo bar

# Match if any term is present
find-stuff search --db D:\work\.find_stuff\index.sqlite3 --any foo bar

# Regex search, case-insensitive
find-stuff search --db D:\work\.find_stuff\index.sqlite3 --regex --ignore-case class(Name)?

# Restrict results to Markdown files
find-stuff search --db D:\work\.find_stuff\index.sqlite3 --ext md token

# Limit to top 10 hits
find-stuff search --db D:\work\.find_stuff\index.sqlite3 --limit 10 http
```

Output format:

```text
<score>\t<absolute-path>
```

Where score is the number of matched postings (occurrences) contributing to the
match.

---

### browse

Interactively navigate indexed repositories, their directories, and files.
Now powered by InquirerPy with fuzzy filtering and colored prompts.

```bash
find-stuff browse --db D:\\work\\.find_stuff\\index.sqlite3
```

Options:

- `--color/--no-color`: enable/disable colored text in prompts and output

Controls:

- Up/Down: move selection
- Type to filter: fuzzy match across items
- Enter: select item
- Change repository: switch to a different repo
- Open this directory in VS Code: launches `code` in current folder
- Back from file view: return from file details
- Quit: exit the browser

When you select a file, the tool shows database metadata and whether the file
has been modified (mtime and hash comparison). Times are printed in a
human‑readable local format (YYYY‑MM‑DD HH:MM:SS).

---

## Library usage

You can also use the Python API:

```python
from pathlib import Path
from find_stuff.indexing import rebuild_index, add_to_index, search_files

root = Path(r"D:\\work")
db = Path(r"D:\\work\\.find_stuff\\index.sqlite3")

rebuild_index(root, db, file_types=("py", "md"))

results = search_files(
    db,
    ["alpha", "beta"],
    require_all_terms=True,
    regex=False,
    case_sensitive=False,
)

for path, score in results:
    print(score, path)
```

---

## Database

This project keeps a compact SQLite database that behaves like a local card
catalog for your code. Each table captures a different aspect of “where did we
look” and “what did we find.” The shape is intentionally simple, so you can
inspect it with any SQLite browser.

### Table: repositories

Think of this as the shelf registry. Each row represents a Git repository
discovered under your chosen root folder. It remembers only the absolute path
of that repository’s root. When you scan again, the tool checks this registry
to avoid duplicating shelves. There’s an internal numeric label for each shelf,
used by other tables to say “this file came from that shelf.”

### Table: files

This is the card catalog of individual files. For every file that Git tracks
and that matches your chosen extensions, we remember a few simple things: which
shelf it belongs to, the neat little path it has inside that shelf so you can
find it again, and the full location on disk that points straight to the file.
Together, these columns say “this precise file, from that repository, lives
here.” The catalog ensures that the same file isn’t listed twice within the
same repository.

### Table: tokens

Imagine a dictionary of every distinct word-like fragment we encountered across
all indexed files. Each entry keeps the exact spelling it had when we saw it,
along with a quiet, lowercased twin that helps us match things without worrying
about capitalization. The important part is that every different fragment
appears only once in this dictionary and gets its own stable identifier for
quick cross-referencing.

### Table: postings

This is the map of where each fragment shows up. For a given file and a given
fragment from the dictionary, we keep a precise spot where it appears: which
line it’s on and where it starts on that line. If the same fragment appears
multiple times in one file, each spot is recorded separately. By tying together
file, fragment, and position, this table is what lets searches be fast and
precise. Internally, the combination of file, fragment, line and column
uniquely identifies each occurrence.

### Table: metadata

This is a tiny drawer for housekeeping notes. It stores small
labeled values that describe the index itself, such as configuration details or
versioning information if needed in the future. It’s intentionally minimal and
meant for tool-level notes rather than content.

---

## Indexing and re-scanning

Building the index is a walk through your chosen root, looking for Git
repositories by spotting their `.git` markers. Each repository is treated as
its own island. For each island, the tool asks Git which files are actually
tracked, and then keeps only the ones whose extensions you selected. Every file
is opened softly with UTF‑8 and errors ignored, then broken into simple
word-like tokens: sequences that look like names in code or natural text. For
every token we encounter, we jot down where it occurred in the file by line and
column. The token dictionary is expanded as needed, and each occurrence is
stored in the postings map. When you run a full rebuild, the previous database
is freshly created so the catalog reflects exactly what you scanned. When you
add to the index, the process is gentler: already-known repositories are
skipped, and only new ones are appended so your catalog grows without being
wiped.

---

## How search works

Searching starts by translating your terms into entries in the token
dictionary. If you request exact matching, the translation is a straight
look‑up, either in original form or in the lowercased variant when you prefer
to ignore case. If you switch to regular expressions, the system takes a quick
stroll through the dictionary and keeps the entries that satisfy your pattern,
using your case preference. Once terms are resolved to token entries, the
search narrows down files. If you asked for all terms, it first finds the set
of files that contain the first term and keeps trimming that set by checking
the others, ending with only the files that have every term. If you asked for
any term, it simply collects all files that have at least one of them. Finally,
it counts how many relevant occurrences contribute to each file and orders
results from most to least evidence. Optional filters, such as limiting to
specific extensions, are applied near the end so you can fine‑tune the list
without rebuilding the index.

---

## Developing

This project is small on purpose and aims for a pleasant contributor experience.

### Requirements

- Python 3.11+
- Git available on PATH for real-world runs (tests mock it)

### Setup

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1   # on Windows PowerShell
pip install -e .[dev]
```

### Common tasks

```bash
# Format
make format

# Lint
make lint

# Tests (type-check + pytest)
make test

# Fix simple lint issues automatically
make delint
```

The CLI entry point is `find_stuff.__main__:cli` and can be invoked as:

```bash
python -m find_stuff --help
```

### Project conventions

- Typed code, small modules, clear names
- Prefer stdlib and a minimal set of dependencies
- Follow ruff formatting and linting configuration in `pyproject.toml`
- Keep public APIs stable; if you change them, update `CHANGELOG.md`

### Release

On the local machine create a package and test it.

```bash
pip install build twine
python -m build
twine check dist/*
```

Change `## [Unreleased]` to the name of the new version in `CHANGELOG.md`,
then create a commit, then create a new tag and push it to GitHub:

```bash
git add .
git commit -m "Release version 0.1.0"

git tag -a v0.1.0 -m "Release version 0.1.0"

git push origin v0.1.0
# or
git push origin --tags
```

In the GitHub repository page create a new Release. This will trigger the
workflow for publishing in PyPi.

---

## License

BSD-3-Clause
