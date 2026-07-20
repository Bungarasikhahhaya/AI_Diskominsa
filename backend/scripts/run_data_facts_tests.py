import os
import pandas as pd
from services import data_facts


def inspect_source(src):
    if not src:
        print("  no source returned")
        return
    if src.startswith("http"):
        print(f"  source is URL: {src}")
        return
    path = os.path.join(data_facts.ROOT, src)
    path = os.path.normpath(path)
    print(f"  loading: {path}")
    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception as e:
        print("  failed to read CSV:", e)
        return

    print("  columns:", list(df.columns[:25]))
    return df


def analyze_query(question, region=None, year=None):
    print('\n== QUERY ==')
    print(question)
    # show top candidate local CSV paths
    try:
        candidates = data_facts._best_candidate_paths(question, top_k=5)
        print('  top candidate paths:')
        for c in candidates[:5]:
            print('   -', c)
    except Exception as e:
        print('  could not compute candidates:', e)
    # If there's a top local CSV candidate, compute the max for the requested year
    try:
        if candidates:
            top_local = None
            for c in candidates:
                if c and not str(c).startswith('http') and os.path.exists(c):
                    top_local = c
                    break
            if top_local:
                print('\n  Inspecting top local candidate for year', year, ':', top_local)
                df_local = pd.read_csv(top_local, low_memory=False)
                cols = list(df_local.columns)
                ycol = data_facts._find_column(cols, data_facts.YEAR_COLUMN_PATTERNS)
                rcol = data_facts._find_column(cols, data_facts.REGION_COLUMN_PATTERNS)
                q_tokens = data_facts._tokens(question)
                metric_token = data_facts._find_metric_token(q_tokens)
                mcol = data_facts._find_best_metric_column(cols, metric_token)
                if mcol is None:
                    mcol = data_facts._find_column(cols, ['jumlah','nilai','total','count'])
                if ycol and year and mcol and rcol:
                    df_y = df_local[df_local[ycol].astype(str).apply(lambda v: data_facts._matches_year_value(v, year))]
                    if not df_y.empty:
                        df_y['_mnum'] = pd.to_numeric(df_y[mcol], errors='coerce')
                        mx = df_y['_mnum'].idxmax()
                        print('  local max row (from top candidate):')
                        print(df_y.loc[mx, [rcol, ycol, mcol]])
                    else:
                        print('  no rows for year in local file')
    except Exception as e:
        print('  failed local inspect:', e)
    ans, src = data_facts.answer(question, region, year)
    print('\n-> data_facts.answer()')
    print('  answer:', ans)
    print('  source:', src)
    df = inspect_source(src)
    if df is None or df is None:
        return

    cols = list(df.columns)
    year_col = data_facts._find_column(cols, data_facts.YEAR_COLUMN_PATTERNS)
    region_col = data_facts._find_column(cols, data_facts.REGION_COLUMN_PATTERNS)
    q_tokens = data_facts._tokens(question)
    metric_token = data_facts._find_metric_token(q_tokens)
    metric_col = data_facts._find_best_metric_column(cols, metric_token)
    print('  resolved columns -> year:', year_col, 'region:', region_col, 'metric:', metric_col)

    if metric_col is None:
        # try generic columns
        for c in ['jumlah', 'nilai', 'total', 'count']:
            candidate = data_facts._find_column(cols, [c])
            if candidate:
                metric_col = candidate
                break

    if metric_col is None:
        print('  cannot determine metric column')
        return

    sel = df
    if region_col and region:
        sel = sel[sel[region_col].astype(str).str.lower().str.contains(str(region).lower(), na=False)]
    if year_col and year:
        sel = sel[sel[year_col].astype(str).apply(lambda v: data_facts._matches_year_value(v, year))]

    print('  rows after region/year filter:', len(sel))
    if len(sel) == 0:
        print('  no rows match the filters')
        return

    # try to coerce metric to numeric for sorting
    try:
        sel['_metric_num'] = pd.to_numeric(sel[metric_col], errors='coerce')
        top = sel.sort_values('_metric_num', ascending=False).head(5)
    except Exception:
        top = sel.head(5)

    print('\n  top rows:')
    with pd.option_context('display.max_columns', 50):
        print(top[[region_col, year_col, metric_col]].head(10))


if __name__ == '__main__':
    queries = [
        (
            'kabupaten apa yang memiliki jumlah penduduk terbanyak di provinsi aceh pada tahun 2021?',
            'aceh',
            '2021',
        ),
        (
            'jumlah penduduk termiskin pada kabupaten aceh barat?',
            'Aceh Barat',
            None,
        ),
    ]

    for q, region, year in queries:
        analyze_query(q, region, year)
