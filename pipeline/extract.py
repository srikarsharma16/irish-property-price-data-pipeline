"""Extract: download a CSO PxStat table as CSV (or read a local CSV)."""
from pathlib import Path
import requests

BASE_URL = ("https://ws.cso.ie/public/api.restful/"
            "PxStat.Data.Cube_API.ReadDataset/{code}/CSV/1.0/en")


def fetch(code: str, raw_dir: str = "data/raw") -> Path:
    """Download table `code` (e.g. HPM09) and save the raw CSV unchanged."""
    Path(raw_dir).mkdir(parents=True, exist_ok=True)
    resp = requests.get(BASE_URL.format(code=code), timeout=60,
                        headers={"User-Agent": "finance-data-pipeline/1.0"})
    resp.raise_for_status()
    path = Path(raw_dir) / f"{code}.csv"
    path.write_bytes(resp.content)  # keep the raw file exactly as received
    return path
