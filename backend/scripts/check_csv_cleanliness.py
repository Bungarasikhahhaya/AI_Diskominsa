import os
import glob
import csv
import pandas as pd

CSV_DIR = "data/csv"


def analyze_file(path):
    print("\n=== File: {} ===".format(path))

    # Quick structural check using csv.reader to detect inconsistent row lengths
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            lengths = []
            for i, row in enumerate(reader):
                lengths.append(len(row))
    except Exception as e:
        print(f"Could not open/read file with csv.reader: {e}")
        return

    if not lengths:
        print("Empty file")
        return

    header_len = lengths[0]
    total_rows = len(lengths) - 1  # excluding header
    inconsistent_indices = [i + 1 for i, l in enumerate(lengths) if l != header_len]
    print(f"Header columns: {header_len}")
    print(f"Total rows (excluding header): {total_rows}")
    print(f"Rows with inconsistent column count: {len(inconsistent_indices)}")
    if inconsistent_indices:
        print("Sample inconsistent row numbers:", inconsistent_indices[:10])

    # Load with pandas for deeper checks
    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception as e:
        print(f"pandas.read_csv failed: {e}")
        return

    print(f"pandas read shape: {df.shape}")
    print("Columns:", list(df.columns))

    # Missing values summary
    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_summary = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
    print("\nMissing values per column:")
    print(missing_summary.sort_values("missing_count", ascending=False).to_string())

    # Duplicates
    dup_count = df.duplicated().sum()
    print(f"\nDuplicate rows: {dup_count}")

    # Inferred dtypes
    print("\nInferred dtypes:")
    print(df.dtypes)

    # For numeric-able columns, show coercion failures
    numeric_candidates = [c for c in df.columns if df[c].dtype == 'object']
    if numeric_candidates:
        print("\nChecking object columns for numeric values (coercion failures):")
        for c in numeric_candidates:
            coerced = pd.to_numeric(df[c], errors='coerce')
            non_numeric = coerced.isna() & df[c].notna()
            cnt = non_numeric.sum()
            if cnt:
                pct = round(cnt / len(df) * 100, 2)
                samples = df.loc[non_numeric, c].astype(str).unique()[:5].tolist()
                print(f"- {c}: {cnt} non-numeric ( {pct}% ) — sample: {samples}")

    # Show sample rows
    print("\nSample rows:")
    print(df.head(5).to_string(index=False))


if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
    if not files:
        print("No CSV files found in data/csv")
    for p in files:
        analyze_file(p)
