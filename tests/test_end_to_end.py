import pandas as pd
from sqlalchemy import text
from pipeline.clean import tidy, validate
from pipeline.load import get_engine, init_schema, load
from tests.test_clean import sample


def test_load_is_idempotent(tmp_path):
    engine = get_engine(f"sqlite:///{tmp_path/'t.db'}")
    init_schema(engine)
    clean, rej, summ = validate(tidy(sample(), "TEST"))
    for _ in range(2):                       # run twice -> must not duplicate rows
        load(engine, "TEST", clean, rej, summ)
    with engine.connect() as c:
        n = c.execute(text("SELECT COUNT(*) FROM fact_observation")).scalar()
        runs = c.execute(text("SELECT COUNT(*) FROM dq_run_log")).scalar()
    assert n == len(clean) and runs == 2
