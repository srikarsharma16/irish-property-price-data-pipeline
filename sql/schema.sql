CREATE TABLE IF NOT EXISTS fact_observation (
    dataset_code TEXT    NOT NULL,
    statistic    TEXT    NOT NULL,
    category     TEXT    NOT NULL,
    period_date  DATE    NOT NULL,
    year         INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    unit         TEXT,
    value        NUMERIC NOT NULL,
    PRIMARY KEY (dataset_code, statistic, category, period_date)
);

CREATE TABLE IF NOT EXISTS dq_rejects (
    dataset_code TEXT,
    reason       TEXT,
    statistic    TEXT,
    category     TEXT,
    period_code  TEXT,
    value_raw    TEXT
);

CREATE TABLE IF NOT EXISTS dq_run_log (
    dataset_code  TEXT,
    run_ts        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rows_raw      INTEGER,
    rows_clean    INTEGER,
    rows_rejected INTEGER
);
