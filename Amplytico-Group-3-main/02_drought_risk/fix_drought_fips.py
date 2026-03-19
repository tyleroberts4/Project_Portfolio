#!/usr/bin/env python3
"""Fix county_fips to 5-digit zero-padded strings in drought weekly CSV.

This script is small enough to run during review. For this submission repo, a
newest week52only file is included compressed as `.csv.gz`.
"""

import argparse
import csv
import gzip
from pathlib import Path


def format_fips(value):
    """Convert FIPS to 5-digit zero-padded string."""
    if value is None or (isinstance(value, float) and (value != value or value == 0)):
        return "00000"
    s = str(int(float(value))).strip()
    return s.zfill(5) if len(s) <= 5 else s[:5]


def _open_text(path: Path, mode: str):
    if str(path).endswith(".gz"):
        # gzip.open needs explicit text mode ('rt'/'wt') for encoding/newline.
        if mode == "r":
            gz_mode = "rt"
        elif mode == "w":
            gz_mode = "wt"
        elif mode == "a":
            gz_mode = "at"
        else:
            gz_mode = mode + "t"
        return gzip.open(path, gz_mode, encoding="utf-8", newline="")
    return open(path, mode, encoding="utf-8", newline="")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix county_fips formatting in drought weekly CSV.")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input drought weekly CSV or CSV.GZ.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output drought weekly CSV or CSV.GZ.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    default_in = base / "drought_weekly_by_county_2015_2024_week52only_fixed_2.0.csv.gz"
    if args.input is None:
        args.input = default_in
    if args.output is None:
        if str(args.input).endswith(".gz"):
            args.output = args.input.with_name(args.input.stem + "_fixed_fips.csv.gz")
        else:
            args.output = args.input.with_name(args.input.stem + "_fixed_fips.csv")

    if not args.input.is_file():
        raise FileNotFoundError(f"Input not found: {args.input}")

    with _open_text(args.input, "r") as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        if "county_fips" not in (fieldnames or []):
            raise SystemExit("Column 'county_fips' not found")

        with _open_text(args.output, "w") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                row["county_fips"] = format_fips(row.get("county_fips", ""))
                writer.writerow(row)

    print(f"Done. Output: {args.output}")


if __name__ == "__main__":
    main()
