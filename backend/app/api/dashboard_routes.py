from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# dashboard_routes.py -> api -> app -> backend -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


from typing import Optional

def _count_rows(dataset_name: str) -> Optional[int]:
    """Return a dataset row count, preferring Parquet and falling back to CSV."""
    parquet_path = DATA_DIR / f"{dataset_name}.parquet"
    csv_path = DATA_DIR / f"{dataset_name}.csv"

    try:
        if parquet_path.exists():
            return len(pd.read_parquet(parquet_path))
        if csv_path.exists():
            # Count rows without retaining the full CSV in memory.
            return sum(1 for _ in csv_path.open("r", encoding="utf-8-sig")) - 1
        return None
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read dataset '{dataset_name}': {exc}",
        ) from exc


@router.get("/summary")
def dashboard_summary():
    """Return counts from the generated influencer and campaign datasets."""
    influencers = _count_rows("influencers")
    campaigns = _count_rows("campaigns")

    missing = []
    if influencers is None:
        missing.append("influencers.csv or influencers.parquet")
    if campaigns is None:
        missing.append("campaigns.csv or campaigns.parquet")

    if missing:
        raise HTTPException(
            status_code=404,
            detail=(
                "Dashboard datasets not found: "
                + ", ".join(missing)
                + f". Expected them under {DATA_DIR}"
            ),
        )

    return {
        "influencers_indexed": influencers,
        "campaigns_analyzed": campaigns,
        "data_source": "synthetic",
    }
