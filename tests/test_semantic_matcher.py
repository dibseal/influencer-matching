
import pytest

from backend.app.ml.evaluation import (
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
)


def test_precision_at_k():
    assert precision_at_k(
        ["A", "B", "C", "D"],
        {"A", "C"},
        k=4,
    ) == 0.5


def test_recall_at_k():
    assert recall_at_k(
        ["A", "B", "C"],
        {"A", "C", "E"},
        k=3,
    ) == pytest.approx(2 / 3)


def test_ndcg_at_k_perfect_ranking():
    score = ndcg_at_k(
        ["A", "B", "C"],
        {"A": 3, "B": 2, "C": 1},
        k=3,
    )
    assert score == pytest.approx(1.0)


def test_ndcg_penalizes_poor_ranking():
    score = ndcg_at_k(
        ["C", "B", "A"],
        {"A": 3, "B": 2, "C": 1},
        k=3,
    )
    assert 0 <= score < 1


def test_invalid_k():
    with pytest.raises(ValueError):
        precision_at_k(["A"], {"A"}, k=0)
