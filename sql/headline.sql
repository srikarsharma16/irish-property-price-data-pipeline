SELECT category, 'peak (before 2010)' AS label, period_date, value FROM (
  SELECT category, period_date, value,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY value DESC) AS rn
  FROM fact_observation
  WHERE statistic = 'Residential Property Price Index'
    AND (category LIKE 'National%all residential%' OR category = 'Dublin - all residential properties')
    AND period_date < '2010-01-01') WHERE rn = 1
UNION ALL
SELECT category, 'trough (2009-2014)', period_date, value FROM (
  SELECT category, period_date, value,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY value ASC) AS rn
  FROM fact_observation
  WHERE statistic = 'Residential Property Price Index'
    AND (category LIKE 'National%all residential%' OR category = 'Dublin - all residential properties')
    AND period_date BETWEEN '2009-01-01' AND '2014-12-31') WHERE rn = 1
UNION ALL
SELECT category, 'latest', period_date, value FROM (
  SELECT category, period_date, value,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY period_date DESC) AS rn
  FROM fact_observation
  WHERE statistic = 'Residential Property Price Index'
    AND (category LIKE 'National%all residential%' OR category = 'Dublin - all residential properties')) WHERE rn = 1
ORDER BY category, label;
