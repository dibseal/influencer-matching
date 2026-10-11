
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT_DIR / "config" / "ml_config.json"


class SemanticMatcher:
    def __init__(self, config_path=None):
        path = Path(config_path) if config_path else DEFAULT_CONFIG

        with path.open("r", encoding="utf-8") as file:
            self.config = json.load(file)

        self.model = SentenceTransformer(
            self.config.get(
                "embedding_model",
                "sentence-transformers/all-MiniLM-L6-v2",
            )
        )

        self.semantic_weight = float(
            self.config.get("semantic_weight", 0.30)
        )

        if not 0 <= self.semantic_weight <= 1:
            raise ValueError("semantic_weight must be between 0 and 1")

    @staticmethod
    def _parse_list(value):
        if isinstance(value, list):
            return [str(item) for item in value]

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                pass

            return [item.strip() for item in value.split(",") if item.strip()]

        return []

    def _influencer_text(self, influencer, audiences):
        influencer_id = influencer["influencer_id"]

        rows = audiences[
            audiences["influencer_id"] == influencer_id
        ]

        interests = []
        for value in rows.get("interests", []):
            interests.extend(self._parse_list(value))

        return (
            f"Platform: {influencer['platform']}. "
            f"Creator niche: {influencer['primary_niche']}. "
            f"Location: {influencer['location']}. "
            f"Audience interests: {', '.join(sorted(set(interests)))}."
        )

    def score(self, campaign, influencers, audiences):
        """Return influencer IDs with semantic similarity scores."""

        if influencers.empty:
            return pd.DataFrame(
                columns=["influencer_id", "semantic_similarity"]
            )

        target_interests = self._parse_list(
            campaign.get("target_interests", [])
        )

        campaign_text = (
            f"Campaign category: {campaign['target_category']}. "
            f"Campaign objective: {campaign.get('objective', '')}. "
            f"Target location: {campaign['target_location']}. "
            f"Target audience ages: {campaign['target_age_min']} "
            f"to {campaign['target_age_max']}. "
            f"Target interests: {', '.join(target_interests)}."
        )

        influencer_texts = [
            self._influencer_text(row, audiences)
            for _, row in influencers.iterrows()
        ]

        embeddings = self.model.encode(
            [campaign_text, *influencer_texts],
            normalize_embeddings=True,
            convert_to_numpy=True,
            batch_size=int(self.config.get("batch_size", 64)),
        )

        similarities = cosine_similarity(
            embeddings[0:1],
            embeddings[1:],
        )[0]

        # Cosine similarity is in [-1, 1]. Map to [0, 100].
        scores = np.clip((similarities + 1) * 50, 0, 100)

        return pd.DataFrame({
            "influencer_id": influencers["influencer_id"].to_numpy(),
            "semantic_similarity": np.round(scores, 2),
        }).sort_values(
            "semantic_similarity",
            ascending=False,
        ).reset_index(drop=True)
