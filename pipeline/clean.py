"""Transform: reshape a PxStat CSV into one tidy table and validate it.

Every rule that removes a row records WHY in a rejects table, so nothing
is dropped silently.
"""
import re
import pandas as pd

CODE_COL = re.compile(r"^C\d+V\d+$")          # e.g. C02803V03373 (dimension code)
TIME_CODE = re.compile(r"^(\d{4})M(\d{2})$")  # e.g. 2005M01


def _find(cols, pred):
    return next((c for c in cols if pred(c)), None)


def tidy(raw: pd.DataFrame, dataset_code: str) -> pd.DataFrame:
    """Rename/reshape raw PxStat columns into a consistent tidy layout."""
    raw = raw.copy()
    raw.columns = [c.strip() for c in raw.columns]
    cols = list(raw.columns)

    stat = _find(cols, lambda c: c.lower() == "statistic label") or \
           _find(cols, lambda c: c.lower() == "statistic")
    tcode = _find(cols, lambda c: c.upper().startswith("TLIST"))
    tlabel = _find(cols, lambda c: c.lower() in ("month", "year", "quarter"))
    unit = _find(cols, lambda c: c.upper() == "UNIT")
    val = _find(cols, lambda c: c.upper() == "VALUE")
    if not (stat and tcode and val):
        raise ValueError(f"Unexpected layout for {dataset_code}: {cols}")

    used = {stat, tcode, tlabel, unit, val, "STATISTIC"}
    dims = [c for c in cols if c not in used and not CODE_COL.match(c)]

    out = pd.DataFrame({
        "dataset_code": dataset_code,
        "statistic": raw[stat],
        "category": raw[dims].astype(str).agg(" | ".join, axis=1) if dims else "All",
        "period_code": raw[tcode].astype(str),
        "period_label": raw[tlabel] if tlabel else raw[tcode],
        "unit": raw[unit] if unit else None,
        "value_raw": raw[val],
    })
    for c in ("statistic", "category", "unit"):
        out[c] = out[c].astype("string").str.strip()
    return out


def _parse_period(row_code, row_label):
    m = TIME_CODE.match(str(row_code))
    if m:
        return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
    return pd.to_datetime(str(row_label), format="%Y %B", errors="coerce")


def validate(df: pd.DataFrame):
    """Apply data-quality rules. Returns (clean_df, rejects_df, summary_dict)."""
    df = df.copy().reset_index(drop=True)
    rejects = []

    def reject(mask, reason):
        nonlocal df
        if mask.any():
            r = df[mask].copy()
            r["reason"] = reason
            rejects.append(r)
        df = df[~mask]

    n_raw = len(df)

    # Rule 1: period must parse to a real month
    df["period_date"] = pd.to_datetime(
        [_parse_period(c, l) for c, l in zip(df.period_code, df.period_label)], errors="coerce")
    reject(df.period_date.isna(), "unparseable period")

    # Rule 2: value must be numeric; distinguish "series not started" from real gaps
    df["value"] = pd.to_numeric(df.value_raw, errors="coerce")
    first = (df[df.value.notna()].groupby(["statistic", "category"])
               .period_date.min().rename("first_valid"))
    df = df.merge(first, on=["statistic", "category"], how="left")
    reject(df.value.isna() & (df.period_date < df.first_valid),
           "series not yet published (before first valid value)")
    reject(df.value.isna(), "missing value inside series")

    # Rule 3: negatives are invalid unless the unit is a % change
    is_pct = df.unit.fillna("").str.contains("%|per cent|percent", case=False, regex=True)
    reject((df.value < 0) & ~is_pct, "negative value in a non-% series")

    # Rule 4: duplicate observations (same series + period) - keep first
    key = ["dataset_code", "statistic", "category", "period_date"]
    reject(df.duplicated(subset=key, keep="first"), "duplicate observation")

    df["year"] = df.period_date.dt.year
    df["month"] = df.period_date.dt.month
    clean = df[["dataset_code", "statistic", "category", "period_date",
                "year", "month", "unit", "value"]].reset_index(drop=True)
    clean["period_date"] = clean.period_date.dt.strftime("%Y-%m-%d")

    rcols = ["dataset_code", "reason", "statistic", "category", "period_code", "value_raw"]
    rej = pd.concat(rejects)[rcols] if rejects else pd.DataFrame(columns=rcols)
    rej["value_raw"] = rej["value_raw"].astype(str)

    summary = {"rows_raw": n_raw, "rows_clean": len(clean), "rows_rejected": len(rej),
               "by_reason": rej.reason.value_counts().to_dict()}
    return clean, rej.reset_index(drop=True), summary
