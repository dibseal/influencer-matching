
import json

import pandas as pd
import pytest

from backend.app.data_generation.generator import (
    generate_datasets,
    validate_datasets,
)


@pytest.fixture
def small_config(tmp_path):
    config = {
        "seed": 42,
        "output_dir": "data/synthetic",
        "formats": ["csv"],
        "record_counts": {
            "influencers": 20,
            "audience_segments": 30,
            "brands": 4,
            "products": 8,
            "brand_affinity": 30,
            "campaigns": 5,
            "campaign_performance": 25,
        },
    }

    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    return config_path


def test_expected_record_counts(small_config, tmp_path):
    datasets = generate_datasets(
        config_path=small_config,
        output_dir=tmp_path / "output",
        formats=["csv"],
    )

    assert len(datasets["influencers"]) == 20
    assert len(datasets["audience_segments"]) == 30
    assert len(datasets["brands"]) == 4
    assert len(datasets["products"]) == 8
    assert len(datasets["brand_affinity"]) == 30
    assert len(datasets["campaigns"]) == 5
    assert len(datasets["campaign_performance"]) == 25



def test_foreign_keys_and_business_rules(small_config, tmp_path):
    datasets = generate_datasets(
        config_path=small_config,
        output_dir=tmp_path / "output",
        formats=["csv"],
    )

    validate_datasets(datasets)

    performance = datasets["campaign_performance"]

    assert performance["performance_id"].is_unique
    assert (performance["spend"] >= 0).all()
    assert (
        performance["conversions"] <= performance["clicks"]
    ).all()
    assert (
        performance["reach"] <= performance["impressions"]
    ).all()



def test_csv_files_are_created(small_config, tmp_path):
    output_dir = tmp_path / "output"

    generate_datasets(
        config_path=small_config,
        output_dir=output_dir,
        formats=["csv"],
    )

    expected_files = [
        "influencers.csv",
        "audience_segments.csv",
        "brands.csv",
        "products.csv",
        "brand_affinity.csv",
        "campaigns.csv",
        "campaign_performance.csv",
    ]

    for filename in expected_files:
        assert (output_dir / filename).exists()


def test_reproducible_influencer_data(small_config, tmp_path):
    first = generate_datasets(
        config_path=small_config,
        output_dir=tmp_path / "first",
        formats=["csv"],
    )

    second = generate_datasets(
        config_path=small_config,
        output_dir=tmp_path / "second",
        formats=["csv"],
    )

    pd.testing.assert_frame_equal(
        first["influencers"],
        second["influencers"],
    )
