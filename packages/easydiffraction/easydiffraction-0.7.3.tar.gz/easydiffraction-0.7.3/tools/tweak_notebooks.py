"""Insert a bootstrap code cell as the first cell of every notebook.

Usage::
        python tools/tweak_notebooks.py tutorials/ [more_paths ...]

The bootstrap cell:
- Checks if ``easydiffraction`` is importable; if not, installs it
    with the ``visualization`` extra.
- Adds the tag ``hide-in-docs``.
- Idempotent: skipped if already present and identical.
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell
from nbformat.validator import normalize

BOOTSTRAP_SOURCE = (
    '# Check if the easydiffraction library is installed.\n'
    "# If not, install it with the 'visualization' extras.\n"
    '# Needed when running remotely (e.g. Colab) where the lib is absent.\n'
    'import builtins\n'
    'import importlib.util\n'
    '\n'
    "if (hasattr(builtins, '__IPYTHON__') and\n"
    "    importlib.util.find_spec('easydiffraction') is None):\n"
    "    !pip install 'easydiffraction[visualization]'\n"
)

BOOTSTRAP_TAG = 'hide-in-docs'


def iter_notebooks(paths: list[Path]):
    for p in paths:
        if p.is_dir():
            yield from (q for q in p.rglob('*.ipynb') if q.is_file())
        elif p.is_file() and p.suffix == '.ipynb':
            yield p


def has_bootstrap_first_cell(nb) -> bool:
    """Return True if the first cell exactly matches our bootstrap
    cell.
    """
    if not nb.cells:
        return False
    first = nb.cells[0]
    if first.cell_type != 'code':
        return False
    if (first.source or '') != BOOTSTRAP_SOURCE:
        return False
    tags = (first.metadata or {}).get('tags', [])
    return BOOTSTRAP_TAG in tags


def ensure_bootstrap(nb) -> bool:
    """Ensure the bootstrap cell exists as the very first cell.

    Returns True if a modification was made.
    """
    if has_bootstrap_first_cell(nb):
        return False

    cell = new_code_cell(
        source=BOOTSTRAP_SOURCE,
        metadata={'tags': [BOOTSTRAP_TAG]},
    )
    nb.cells.insert(0, cell)
    return True


def process_notebook(path: Path) -> int:
    nb = nbformat.read(path, as_version=4)

    # Remove all 'tags' metadata from cells
    for cell in nb.cells:
        if 'tags' in cell.metadata:
            cell.metadata.pop('tags')

    # Add the bootstrap cell if needed
    changed = 0
    if ensure_bootstrap(nb):
        changed += 1

    # Normalize to ensure cell ids exist and structure is valid
    if changed or any('id' not in c for c in nb.cells):
        normalize(nb)
        nbformat.write(nb, path)
    return changed


def main(argv: list[str]) -> int:
    if not argv:
        print('Usage: python tools/tweak_notebooks.py <paths...>', file=sys.stderr)
        return 2

    targets = list(iter_notebooks([Path(p) for p in argv]))
    if not targets:
        print('No .ipynb files found.', file=sys.stderr)
        return 1

    updated = 0
    for nb_path in targets:
        changes = process_notebook(nb_path)
        if changes:
            print(f'UPDATED: {nb_path} (inserted bootstrap cell)')
            updated += 1

    if updated == 0:
        print('No changes needed.')
    else:
        print(f'Done. Files changed: {updated}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
