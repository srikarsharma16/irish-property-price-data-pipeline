# Irish Property Price Data Pipeline

An end-to-end data project: download public Irish statistics from the CSO (Central Statistics Office), clean and validate them in Python, load them into a SQL database, and analyse them with SQL.

**Tools:** Python (Pandas, SQLAlchemy, requests), SQL (SQLite), pytest, Git

## Pipeline

```
CSO PxStat API --> extract.py --> clean.py (tidy + validate) --> load.py --> SQL database --> analysis queries
                   raw CSV kept   rejects logged with reason      idempotent   fact + data-quality tables
```

## Data source

- Central Statistics Office (Ireland) PxStat, licensed CC BY 4.0: https://data.cso.ie
- Table `HPM09`: Residential Property Price Index (base 2015 = 100), monthly, data to July 2026
- 4 statistics (index level, plus 1-, 3- and 12-month % change) across 19 property/region categories
- More tables can be added with `--datasets CODE1 CODE2`

## Project structure

```
pipeline/   extract.py, clean.py, load.py, run_pipeline.py
sql/        schema.sql, analysis.sql, headline.sql
tests/      unit and end-to-end tests (pytest)
data/       raw and processed files (large files git-ignored)
```

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate                                # Windows PowerShell
pip install -r requirements.txt
python -m pipeline.run_pipeline --datasets HPM09      # creates data/finance.db (SQLite)
python -m pytest                                      # run the 5 tests
python run_query.py sql/headline.sql                  # print the headline analysis
```

Any SQLAlchemy database URL can be passed with `--db` (for example PostgreSQL); SQLite is the tested default.

## Data-quality rules

| Rule | Action |
|---|---|
| Period cannot be parsed to a month | Reject, log reason |
| Value missing before the series' first published value | Reject as "series not yet published" |
| Value missing inside a series | Reject as "missing value inside series" |
| Negative value in a non-% series | Reject, log reason |
| Duplicate series + period | Keep first, log the rest |

Every rejected row is stored in `dq_rejects` with its reason, and each run is recorded in `dq_run_log`, so no row disappears silently. Loads are idempotent: re-running replaces a dataset's rows and never duplicates them.

## Data-quality findings

- 20,720 rows downloaded, 17,760 clean, 2,960 rejected (14.3%).
- All 2,960 rejections have the same cause: the value is missing before the series' first published value. Many regional and property-type series only start in 2010-2011, while the national series start in 2005.
- I verified this by checking that every rejected row falls before its series' first valid value. No series has a gap inside it, so these are structural gaps, not data errors.
- The first version of the pipeline labelled these rows only as "missing value". Investigating the cause led me to split the rule so expected gaps and real gaps are reported separately.

## Analysis findings (index base 2015 = 100)

| Series | Pre-2010 peak | Trough | Fall | Latest (Jul 2026) | Latest vs peak |
|---|---|---|---|---|---|
| National | 163.6 (Apr 2007) | 73.4 (Mar 2013) | -55.1% | 208.6 | +27.5% |
| Dublin | 160.0 (Feb 2007) | 64.6 (Feb 2012) | -59.6% | 178.1 | +11.3% |
| National excl. Dublin | 183.7 (May 2007) | 79.8 (May 2013) | -56.6% | 240.7 | +31.0% |

1. **Prices more than halved after the 2007 peak.** The national index fell 55.1% over about six years.
2. **Dublin fell harder and bottomed earlier.** It lost 59.6% and reached its low in February 2012, thirteen months before the national trough.
3. **Dublin has recovered least relative to its peak.** By July 2026 it is 11.3% above its 2007 high, against 27.5% nationally and 31.0% outside Dublin.

Peak is the maximum before 2010 and trough is the minimum between 2009 and 2014, calculated with `sql/headline.sql`.

## Limitations

- The index is nominal (not adjusted for inflation), so recovery in real terms is weaker than shown.
- Only one CSO table is loaded, so the analysis describes prices but not causes such as income, interest rates or supply.

## Next steps

- Build a dashboard (Power BI or Tableau Public) on top of the cleaned data
- Add a second CSO table and join the datasets
- Schedule the pipeline monthly and alert on failed validation
