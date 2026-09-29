"""Run the full ETL:  python -m pipeline.run_pipeline --datasets HPM09"""
import argparse
from pathlib import Path
import pandas as pd
from .extract import fetch
from .clean import tidy, validate
from .load import get_engine, init_schema, load


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["HPM09"], help="CSO table codes")
    ap.add_argument("--db", default="sqlite:///data/finance.db",
                    help="SQLAlchemy URL, e.g. postgresql+psycopg2://user:pw@localhost/finance")
    ap.add_argument("--local-file", help="Use a local CSV instead of downloading (single dataset)")
    args = ap.parse_args()

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    engine = get_engine(args.db)
    init_schema(engine)

    for code in args.datasets:
        path = args.local_file or fetch(code)
        raw = pd.read_csv(path, encoding="utf-8-sig")
        clean, rejects, summary = validate(tidy(raw, code))
        load(engine, code, clean, rejects, summary)
        clean.to_csv(f"data/processed/{code}_clean.csv", index=False)
        rejects.to_csv(f"data/processed/{code}_rejects.csv", index=False)
        print(f"[{code}] raw={summary['rows_raw']} clean={summary['rows_clean']} "
              f"rejected={summary['rows_rejected']} {summary['by_reason']}")


if __name__ == "__main__":
    main()
