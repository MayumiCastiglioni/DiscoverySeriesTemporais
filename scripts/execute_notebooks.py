"""Execute the project notebooks from clean Python kernels and save their outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_NOTEBOOKS = tuple(sorted((PROJECT_ROOT / "notebooks" / "bases").glob("*.ipynb")))
MODEL_NOTEBOOKS = tuple(sorted((PROJECT_ROOT / "notebooks" / "modelos").glob("*.ipynb")))
NOTEBOOKS = BASE_NOTEBOOKS + MODEL_NOTEBOOKS


def execute_notebook(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=600, kernel_name="python3")
    client.execute(cwd=str(PROJECT_ROOT))
    nbformat.write(notebook, path)
    print(f"Executed successfully: {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notebook",
        action="append",
        help="Repository-relative notebook path. Repeat to execute selected notebooks only.",
    )
    args = parser.parse_args()
    if args.notebook:
        notebook_paths = tuple(PROJECT_ROOT / Path(path) for path in args.notebook)
    else:
        notebook_paths = NOTEBOOKS
    if not args.notebook and (len(BASE_NOTEBOOKS) != 5 or len(MODEL_NOTEBOOKS) != 20):
        raise ValueError(
            "Expected five base notebooks and twenty model-training notebooks. "
            "Run scripts/generate_course_notebooks.py first."
        )
    for notebook_path in notebook_paths:
        if not notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")
        execute_notebook(notebook_path)


if __name__ == "__main__":
    main()
