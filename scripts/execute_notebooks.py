"""Execute the project notebooks from clean Python kernels and save their outputs."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = (
    PROJECT_ROOT / "notebooks" / "01_auditoria_e_stl_preliminar.ipynb",
    PROJECT_ROOT / "notebooks" / "02_origens_e_xgboost_piloto.ipynb",
)


def execute_notebook(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=180, kernel_name="python3")
    client.execute(cwd=str(PROJECT_ROOT))
    nbformat.write(notebook, path)
    print(f"Executed successfully: {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    for notebook_path in NOTEBOOKS:
        execute_notebook(notebook_path)


if __name__ == "__main__":
    main()
