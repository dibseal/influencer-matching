
import numpy as np
import pandas as pd


def precision_at_k(ranked_ids, relevant_ids, k=10):
    if k <= 0:
        raise ValueError("k must be positive")

    top_k = list(ranked_ids[:k])

    if not top_k:
        return 0.0

    return sum(item in relevant_ids for item in top_k) / k


def recall_at_k(ranked_ids, relevant_ids, k=10):
    if k <= 0:
        raise ValueError("k must be positive")

    if not relevant_ids:
        return 0.0

    top_k = list(ranked_ids[:k])

    return (
        sum(item in relevant_ids for item in top_k)
        / len(relevant_ids)
    )


def ndcg_at_k(ranked_ids, relevance_by_id, k=10):
    if k <= 0:
        raise ValueError("k must be positive")

    ranked = list(ranked_ids[:k])

    if not ranked:
        return 0.0

    gains = np.array([
        max(0.0, float(relevance_by_id.get(item, 0)))
        for item in ranked
    ])

    discounts = np.log2(np.arange(2, len(ranked) + 2))
    dcg = np.sum(gains / discounts)

    ideal = sorted(
        [max(0.0, float(value)) for value in relevance_by_id.values()],
        reverse=True,
    )[:k]

    if not ideal or max(ideal) == 0:
        return 0.0

    ideal_discounts = np.log2(np.arange(2, len(ideal) + 2))
    idcg = np.sum(np.array(ideal) / ideal_discounts)

    return float(dcg / idcg) if idcg else 0.0


def evaluate_ranking(results, relevance_by_id, k=10):
    """Evaluate a ranked DataFrame with an influencer_id column."""

    if "influencer_id" not in results.columns:
        raise ValueError("results must contain influencer_id")

    ranked_ids = results["influencer_id"].tolist()
    relevant_ids = {
        influencer_id
        for influencer_id, score in relevance_by_id.items()
        if score > 0
    }

    return {
        f"precision@{k}": precision_at_k(
            ranked_ids, relevant_ids, k
        ),
        f"recall@{k}": recall_at_k(
            ranked_ids, relevant_ids, k
        ),
        f"ndcg@{k}": ndcg_at_k(
            ranked_ids, relevance_by_id, k
        ),
    }
