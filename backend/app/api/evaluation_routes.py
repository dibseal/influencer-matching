import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/evaluation", tags=["Model Evaluation"])
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


@router.get("/summary")
def evaluation_summary():
    summary_path = OUTPUT_DIR / "ranking_evaluation_summary.csv"
    detail_path = OUTPUT_DIR / "ranking_evaluation.csv"
    json_path = OUTPUT_DIR / "ranking_evaluation.json"

    if summary_path.exists():
        try:
            frame = pd.read_csv(summary_path)
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Could not read evaluation summary: {}".format(exc)) from exc
        required = {"model", "precision@10", "recall@10", "ndcg@10"}
        if not required.issubset(frame.columns):
            raise HTTPException(status_code=500, detail="Evaluation summary is missing required metric columns.")
        models = []
        for row in frame.to_dict("records"):
            models.append({
                "model": str(row["model"]),
                "precision_at_10": float(row["precision@10"]),
                "recall_at_10": float(row["recall@10"]),
                "ndcg_at_10": float(row["ndcg@10"]),
            })
        return {
            "status": "available",
            "source": summary_path.name,
            "k": 10,
            "models": models,
            "evaluation_cases": int(len(pd.read_csv(detail_path))) if detail_path.exists() else None,
            "note": "Metrics are from the saved evaluation output. The labels are synthetic and should not be interpreted as real-world performance."
        }

    if json_path.exists():
        try:
            with json_path.open("r", encoding="utf-8") as file:
                return {"status": "available", "source": json_path.name, "summary": json.load(file)}
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Could not read evaluation JSON: {}".format(exc)) from exc

    raise HTTPException(status_code=404, detail="Evaluation summary not found. Run backend.app.ml.run_evaluation to generate data/output/ranking_evaluation_summary.csv.")
