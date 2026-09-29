# Building the dashboard (Power BI Desktop, free)

Power BI Desktop is Windows only. On Mac, use Tableau Public (free) with the same steps.

## 1. Connect to the data
- Easiest: Home > Get data > Text/CSV > choose `data/processed/HPM09_clean.csv`
- Or connect to PostgreSQL: Get data > PostgreSQL database > table `fact_observation`
- Also import `HPM09_rejects.csv` for the data-quality page.
- In Power Query, check `period_date` is type Date and `value` is Decimal number.

## 2. Suggested pages
**Page 1: Overview**
- Card: latest index value (filter to the latest `period_date`)
- Line chart: `period_date` (x) vs `value` (y), legend = `category`
- Slicers: `category`, `year`

**Page 2: Year-on-year change**
- Create a measure (DAX):
  `YoY % = DIVIDE( SUM(fact_observation[value]) - CALCULATE(SUM(fact_observation[value]), DATEADD(fact_observation[period_date], -1, YEAR)), CALCULATE(SUM(fact_observation[value]), DATEADD(fact_observation[period_date], -1, YEAR)))`
- Clustered column chart of YoY % by year; mark the peak and the trough.
- Requires a proper date column; if DATEADD complains, add a Date table (Modeling > New table > CALENDARAUTO()).

**Page 3: Data quality**
- Bar chart: count of rejected rows by `reason`
- Table: `dq_run_log` (raw / clean / rejected per run)

## 3. Finish
- Give every visual a clear title and axis label; state the source (CSO, CC BY 4.0) in a text box.
- Export a PNG of each page into `docs/` and link it in the README.
- File > Export > PDF is also useful to attach to a portfolio.
