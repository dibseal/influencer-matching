
import json
from pathlib import Path

import pandas as pd

from backend.app.matching.engine import InfluencerMatchingEngine
from backend.app.ml.semantic_matcher import SemanticMatcher
from backend.app.ml.evaluation import evaluate_ranking


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "synthetic"
OUTPUT_DIR = ROOT_DIR / "data" / "output"
ML_CONFIG = ROOT_DIR / "config" / "ml_config.json"


def load_datasets():
    required = [
        "influencers",
        "audience_segments",
        "brand_affinity",
        "campaigns",
        "campaign_performance",
    ]

    datasets = {}

    for name in required:
        path = DATA_DIR / f"{name}.parquet"

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {path}. "
                "Run the synthetic data generator first."
            )

        datasets[name] = pd.read_parquet(path)

    return datasets


def build_relevance_map(performance, campaign_id):
    """Aggregate observed synthetic relevance by influencer."""
    rows = performance[
        performance["campaign_id"] == campaign_id
    ]

    if rows.empty:
        return {}

    return (
        rows.groupby("influencer_id")["synthetic_relevance_score"]
        .mean()
        .to_dict()
    )


def run_evaluation(max_campaigns=50, k=10):
    datasets = load_datasets()

    influencers = datasets["influencers"]
    audiences = datasets["audience_segments"]
    affinity = datasets["brand_affinity"]
    campaigns = datasets["campaigns"]
    performance = datasets["campaign_performance"]

    baseline_engine = InfluencerMatchingEngine()
    semantic_engine = SemanticMatcher()

    records = []

    # Evaluate only campaigns with synthetic observed outcomes.
    observed_campaign_ids = set(performance["campaign_id"])
    evaluation_campaigns = campaigns[
        campaigns["campaign_id"].isin(observed_campaign_ids)
    ].head(max_campaigns)

    for _, campaign_row in evaluation_campaigns.iterrows():
        campaign = campaign_row.to_dict()

        relevance = build_relevance_map(
            performance, campaign["campaign_id"]
        )

        if not relevance:
            continue

        baseline_results = baseline_engine.match(
            campaign,
            influencers,
            audiences,
            affinity,
            performance,
        )

        # Apply the same eligibility constraints as the baseline.
        eligible_ids = set(baseline_results["influencer_id"])
        eligible_influencers = influencers[
            influencers["influencer_id"].isin(eligible_ids)
        ].copy()

        if eligible_influencers.empty:
            continue

        semantic_results = semantic_engine.score(
            campaign,
            eligible_influencers,
            audiences,
        )

        # Evaluate both methods against the same candidate pool.
        baseline_relevance = {
            influencer_id: relevance[influencer_id]
            for influencer_id in baseline_results["influencer_id"]
            if influencer_id in relevance
        }

        semantic_relevance = {
            influencer_id: relevance[influencer_id]
            for influencer_id in semantic_results["influencer_id"]
            if influencer_id in relevance
        }

        baseline_metrics = evaluate_ranking(
            baseline_results,
            baseline_relevance,
            k=k,
        )

        semantic_metrics = evaluate_ranking(
            semantic_results,
            semantic_relevance,
            k=k,
        )

        for model_name, metrics in [
            ("weighted_baseline", baseline_metrics),
            ("semantic_matching", semantic_metrics),
        ]:
            records.append({
                "campaign_id": campaign["campaign_id"],
                "model": model_name,
                "eligible_candidates": len(eligible_ids),
                **metrics,
            })

    if not records:
        raise ValueError(
            "No campaigns could be evaluated. Check the relationship "
            "between campaigns and campaign_performance."
        )

    results = pd.DataFrame(records)

    metric_columns = [
        column for column in results.columns
        if column.startswith(("precision@", "recall@", "ndcg@"))
    ]

    summary = (
        results.groupby("model")[metric_columns]
        .mean()
        .reset_index()
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results.to_csv(
        OUTPUT_DIR / "ranking_evaluation.csv",
        index=False,
    )
    summary.to_csv(
        OUTPUT_DIR / "ranking_evaluation_summary.csv",
        index=False,
    )

    report = {
        "campaigns_evaluated": int(
            results["campaign_id"].nunique()
        ),
        "k": k,
        "metrics_by_model": summary.to_dict("records"),
    }

    with (OUTPUT_DIR / "ranking_evaluation.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=2)

    print("\nEvaluation completed.")
    print(summary.to_string(index=False))
    print(f"\nResults saved to: {OUTPUT_DIR}")

    return results, summary


if __name__ == "__main__":
    run_evaluation()
