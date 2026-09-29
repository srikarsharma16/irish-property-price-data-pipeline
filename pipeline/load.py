"""Load: write clean data + data-quality logs into SQL (SQLite or PostgreSQL)."""
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text


def get_engine(url: str):
    return create_engine(url)


def init_schema(engine, schema_path="sql/schema.sql"):
    statements = [s.strip() for s in Path(schema_path).read_text().split(";") if s.strip()]
    with engine.begin() as conn:
        for s in statements:
            conn.execute(text(s))


def load(engine, dataset_code, clean: pd.DataFrame, rejects: pd.DataFrame, summary: dict):
    """Idempotent load: re-running for a dataset replaces its rows (no duplicates)."""
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM fact_observation WHERE dataset_code = :c"), {"c": dataset_code})
        conn.execute(text("DELETE FROM dq_rejects WHERE dataset_code = :c"), {"c": dataset_code})
        clean.to_sql("fact_observation", conn, if_exists="append", index=False)
        rejects.to_sql("dq_rejects", conn, if_exists="append", index=False)
        conn.execute(
            text("INSERT INTO dq_run_log (dataset_code, rows_raw, rows_clean, rows_rejected) "
                 "VALUES (:c, :r, :k, :x)"),
            {"c": dataset_code, "r": summary["rows_raw"],
             "k": summary["rows_clean"], "x": summary["rows_rejected"]})
