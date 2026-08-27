"""
Fix relationship CSVs so their foreign keys land inside the actual node ID
ranges. The raw Kaggle "starter pack" tables were generated independently
per-file, so cross-file FK columns (e.g. cards.csv's cardholder_id) reference
a much wider ID space than the number of nodes that actually exist. Only
foreign keys that happened to fall inside the valid range matched during
import (~2.5% of rows).

This script deterministically remaps each out-of-range FK into
[1, target_count] via modulo. Any FK already in range maps to itself
(identity), so it's safe to re-run and won't disturb relationships that
already matched.
"""

import csv
from pathlib import Path

IMPORT_DIR = Path(__file__).parent / "import"

NODE_COUNTS = {
    "Cardholder": 439,
    "Card": 593,
    "Merchant": 366,
    "Transaction": 4398,
    "FraudCase": 967,
}


def remap(raw_id: int, target_count: int) -> int:
    return ((raw_id - 1) % target_count) + 1


def fix_file(filename, start_target=None, end_target=None):
    path = IMPORT_DIR / filename
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    changed = 0
    for row in rows:
        if start_target:
            new_val = remap(int(row[":START_ID"]), NODE_COUNTS[start_target])
            if new_val != int(row[":START_ID"]):
                changed += 1
            row[":START_ID"] = str(new_val)
        if end_target:
            new_val = remap(int(row[":END_ID"]), NODE_COUNTS[end_target])
            if new_val != int(row[":END_ID"]):
                changed += 1
            row[":END_ID"] = str(new_val)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[":START_ID", ":END_ID", ":TYPE"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"{filename}: remapped {changed} of {len(rows)} FK values")


def main():
    # owns.csv: START_ID -> cardholder_id (FK, needs remap), END_ID -> card_id (own PK, fine)
    fix_file("owns.csv", start_target="Cardholder")

    # made.csv: START_ID -> card_id (FK, needs remap), END_ID -> transaction_id (own PK, fine)
    fix_file("made.csv", start_target="Card")

    # at_merchant.csv: START_ID -> transaction_id (own PK, fine), END_ID -> merchant_id (FK, needs remap)
    fix_file("at_merchant.csv", end_target="Merchant")

    # has_fraud.csv: START_ID -> transaction_id (FK, needs remap), END_ID -> fraud_case_id (own PK, fine)
    fix_file("has_fraud.csv", start_target="Transaction")

    print("\nDone. Now re-run: python import_data.py")


if __name__ == "__main__":
    main()