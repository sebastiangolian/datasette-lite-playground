"""Build poland.db (SQLite) from data/cities.csv and data/voivodeships.json.

Usage: python3 scripts/build_db.py <output.db>
Standard library only, so it runs as-is in GitHub Actions.
"""

import csv
import json
import sqlite3
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def build(output: Path) -> None:
    output.unlink(missing_ok=True)
    db = sqlite3.connect(output)
    db.executescript((DATA_DIR / "schema.sql").read_text(encoding="utf-8"))
    db.execute(
        """
        CREATE TABLE voivodeships (
          name TEXT PRIMARY KEY,
          capital TEXT NOT NULL,
          area_km2 INTEGER
        )
        """
    )

    with open(DATA_DIR / "cities.csv", encoding="utf-8", newline="") as f:
        db.executemany(
            "INSERT INTO cities VALUES (:id, :name, :voivodeship, :population, :latitude, :longitude)",
            csv.DictReader(f),
        )

    voivodeships = json.loads((DATA_DIR / "voivodeships.json").read_text(encoding="utf-8"))
    db.executemany("INSERT INTO voivodeships VALUES (:name, :capital, :area_km2)", voivodeships)

    db.commit()
    counts = {t: db.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("cities", "voivodeships")}
    db.close()
    print(f"Built {output}: {counts}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: build_db.py <output.db>")
    build(Path(sys.argv[1]))
