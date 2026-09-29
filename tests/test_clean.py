"""Unit tests use a tiny hand-made table shaped like a CSO PxStat CSV."""
import pandas as pd
from pipeline.clean import tidy, validate


def sample():
    return pd.DataFrame({
        "STATISTIC": ["S1"] * 7,
        "Statistic Label": ["Residential Property Price Index"] * 7,
        "TLIST(M1)": ["2005M01", "2005M02", "2005M02", "2005M03", "BAD", "2005M04", "2005M05"],
        "Month": ["2005 January", "2005 February", "2005 February", "2005 March",
                  "not a date", "2005 April", "2005 May"],
        "C02803V03373": ["-"] * 7,
        "Type of Residential Property": ["National - all residential properties "] * 7,
        "UNIT": ["Base (Jan 2005=100)"] * 7,
        "VALUE": [100.0, 101.5, 101.5, None, 103.0, -5.0, 104.2],
    })


def test_tidy_layout():
    t = tidy(sample(), "TEST")
    assert {"dataset_code", "statistic", "category", "period_code", "value_raw"} <= set(t.columns)
    assert t.category.iloc[0] == "National - all residential properties"  # whitespace stripped


def test_validation_rules_and_counts():
    clean, rej, s = validate(tidy(sample(), "TEST"))
    assert s["rows_raw"] == 7
    assert s["rows_clean"] + s["rows_rejected"] == 7          # nothing lost silently
    reasons = set(rej.reason)
    assert "duplicate observation" in reasons
    assert "missing value inside series" in reasons
    assert "unparseable period" in reasons
    assert "negative value in a non-% series" in reasons
    assert len(clean) == 3 and clean.period_date.is_unique


def test_negative_allowed_for_percent_series():
    df = sample().iloc[[0]].copy()
    df["UNIT"], df["VALUE"] = "%", -2.5
    clean, rej, _ = validate(tidy(df, "TEST"))
    assert len(clean) == 1 and len(rej) == 0
    
    
def test_leading_gap_is_labelled_not_yet_published():
    df = sample().iloc[[0, 1]].copy()      # 2005M01 and 2005M02
    df.loc[df.index[0], "VALUE"] = None    # first month has no value
    clean, rej, _ = validate(tidy(df, "TEST"))
    assert list(rej.reason) == ["series not yet published (before first valid value)"]
    assert len(clean) == 1
