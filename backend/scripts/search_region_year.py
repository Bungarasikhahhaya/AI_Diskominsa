import glob
import pandas as pd
from services import data_facts
import os

region = 'Aceh Utara'
year = '2012'
csvs = glob.glob(os.path.join(data_facts.CSV_DIR, '*.csv'))
print('Searching', len(csvs), 'CSV files for', region, year)
for path in csvs:
    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception:
        continue
    cols = list(df.columns)
    rcol = data_facts._find_column(cols, data_facts.REGION_COLUMN_PATTERNS)
    ycol = data_facts._find_column(cols, data_facts.YEAR_COLUMN_PATTERNS)
    if rcol is None or ycol is None:
        continue
    sel = df[df[rcol].astype(str).str.lower().str.contains(region.lower(), na=False)]
    sel = sel[sel[ycol].astype(str).apply(lambda v: data_facts._matches_year_value(v, year))]
    if not sel.empty:
        print('\nFound in:', path)
        print('Columns:', rcol, ycol)
        print(sel.head(20))
