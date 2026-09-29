# Irish Finance Data Pipeline & Dashboard

An end-to-end data project: download public Irish statistics (CSO PxStat), clean and validate them in Python,
load them into a SQL database, analyse them with SQL, and present the results in a dashboard.

**Tools:** Python (Pandas, SQLAlchemy), SQL (SQLite / PostgreSQL), Power BI (or Tableau Public), pytest

## Pipeline
```
CSO PxStat API --> extract.py --> clean.py (tidy + validate) --> load.py --> SQL database --> analysis.sql --> dashboard
                   raw CSV kept   rejects logged with reason      idempotent   fact + DQ tables
```

## Data source
- Central Statistics Office (Ireland) PxStat, licensed CC BY 4.0: https://data.cso.ie
- Starting table: `HPM09` Residential Property Price Index
- Add more tables with `--datasets CODE1 CODE2` (find codes on data.cso.ie)

## How to run
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pipeline.run_pipeline --datasets HPM09        # creates data/finance.db (SQLite)
python -m pytest                                        # run the tests
```
PostgreSQL: `--db postgresql+psycopg2://user:password@localhost:5432/finance`
Then run the queries in `sql/analysis.sql`. Clean CSVs for the dashboard are written to `data/processed/`.

## Data-quality rules
| Rule | Action |
|---|---|
| Period cannot be parsed to a month | Reject, log reason |
| Value missing or non-numeric | Reject, log reason |
| Negative value in a non-% series | Reject, log reason |
| Duplicate series + period | Keep first, log the rest |

Every rejected row is stored in `dq_rejects` with its reason, and each run is recorded in `dq_run_log`,
so no row disappears silently. Loads are idempotent: re-running does not create duplicates.

## Findings from my run
<!-- FILL THIS IN from your real output. Do not invent numbers. -->
- Rows downloaded / clean / rejected: `__ / __ / __`
- Issues found and how they were handled: `...`
- Key insights from the SQL analysis (2-3 bullets): `...`

## Dashboard
<!-- Add a screenshot: docs/dashboard.png -->
See `docs/dashboard_guide.md` for how it was built.

## What I would do next
- Add a second CSO table and join the two datasets
- Schedule the pipeline to run monthly and alert on failed validation
