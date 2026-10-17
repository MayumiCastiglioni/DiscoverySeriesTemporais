"""Run project checks with the local src package available."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"


def main() -> None:
    sys.path.insert(0, str(SOURCE_ROOT))
    suite = unittest.defaultTestLoader.discover(str(PROJECT_ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
