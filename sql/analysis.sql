-- Run these after the pipeline has loaded data. Works on SQLite (3.25+) and PostgreSQL.

-- 0. Explore first: what series and units exist? Use these exact values in the queries below.
SELECT DISTINCT statistic, unit FROM fact_observation ORDER BY statistic;
SELECT DISTINCT category FROM fact_observation ORDER BY category;

-- 1. Latest value per series
SELECT f.statistic, f.category, f.period_date, f.value
FROM fact_observation f
JOIN (SELECT statistic, category, MAX(period_date) AS max_d
      FROM fact_observation GROUP BY statistic, category) m
  ON f.statistic = m.statistic AND f.category = m.category AND f.period_date = m.max_d
ORDER BY f.statistic, f.category;

-- 2. Year-on-year % change with a window function
--    (replace the statistic name with one returned by query 0)
SELECT category, period_date, value,
       ROUND(100.0 * (value - LAG(value, 12) OVER w) / LAG(value, 12) OVER w, 2) AS yoy_pct
FROM fact_observation
WHERE statistic = 'Residential Property Price Index'
WINDOW w AS (PARTITION BY category ORDER BY period_date)
ORDER BY category, period_date;

-- 3. Annual average per year, ranked within each category
WITH annual AS (
    SELECT category, year, ROUND(AVG(value), 2) AS avg_value
    FROM fact_observation
    WHERE statistic = 'Residential Property Price Index'
    GROUP BY category, year)
SELECT category, year, avg_value,
       RANK() OVER (PARTITION BY category ORDER BY avg_value DESC) AS rank_in_category
FROM annual
ORDER BY category, year;

-- 4. Ten largest month-on-month falls
WITH mom AS (
    SELECT category, period_date, value,
           value - LAG(value) OVER (PARTITION BY category ORDER BY period_date) AS change
    FROM fact_observation
    WHERE statistic = 'Residential Property Price Index')
SELECT * FROM mom WHERE change IS NOT NULL ORDER BY change ASC LIMIT 10;

-- 5. Data-quality summary from the pipeline
SELECT reason, COUNT(*) AS rows_rejected FROM dq_rejects GROUP BY reason;
SELECT * FROM dq_run_log ORDER BY run_ts DESC;
