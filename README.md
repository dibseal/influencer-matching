# InfluenceIQ --- AI-Powered Influencer Matching Platform

> **Project type:** Full-stack proof of concept\
> **Frontend:** React, TypeScript, Vite\
> **Backend:** Python, FastAPI\
> **Data:** Synthetic influencer-marketing datasets in CSV and Parquet
> formats\
> **AI capabilities:** Weighted matching, semantic matching and ranking
> evaluation, LLM-based campaign interpretation and recommendation
> explanations

------------------------------------------------------------------------

## 1. Executive Summary

InfluenceIQ is a proof of concept for helping a brand identify and
compare influencers for a marketing campaign. A user describes the
campaign in natural language, the application interprets the brief into
structured criteria, and the matching service ranks candidate
influencers. The dashboard presents influencer profiles, match scores,
score components, and an AI-generated explanation for an individual
recommendation.

The project demonstrates how a conventional scoring engine can be
combined with semantic matching and a large language model (LLM) to
create a more explainable campaign-planning workflow.

The current implementation uses **synthetic data**. Results are useful
for demonstrating application flow and evaluating implementation
behavior, but they should not be treated as validated marketing
recommendations or evidence of real-world campaign performance.

### The business problem

Choosing influencers manually can require comparing many profiles
against campaign requirements such as marketing objective, social
platform, product category, target audience, engagement quality, brand
affinity, historical campaign performance, and estimated collaboration
cost.

A large candidate set makes consistent comparison difficult. InfluenceIQ
provides a repeatable way to translate campaign requirements into
structured criteria, rank candidates, and explain the factors that
contribute to a recommendation.

### The proposed value

-   **Faster discovery:** shortlist candidates using structured campaign
    criteria.
-   **Consistent comparison:** apply a common scoring framework to
    candidate profiles.
-   **Explainability:** show score components and generate a
    natural-language explanation.
-   **Extensibility:** separate frontend, API, matching, LLM,
    data-generation, and evaluation responsibilities.
-   **Measurability:** evaluate ranking approaches against synthetic
    relevance labels.

------------------------------------------------------------------------

## 2. Goals and Scope

### Goals

1.  Generate a reproducible synthetic dataset for development and
    demonstrations.
2.  Provide a web dashboard for viewing influencer-matching information.
3.  Accept a campaign brief in natural language.
4.  Convert the brief into structured campaign criteria using an LLM.
5.  Rank influencers using a weighted matching engine.
6.  Provide an AI-generated explanation for a selected recommendation.
7.  Evaluate ranking quality using Precision@K, Recall@K, and NDCG@K.
8.  Expose backend functionality through FastAPI endpoints.

### Current proof-of-concept scope

-   Synthetic data generation for influencers, audience segments,
    brands, products, brand affinities, campaigns, and campaign
    performance.
-   CSV and Parquet outputs.
-   A weighted matching engine with component scores.
-   A Sentence Transformers-based semantic matching implementation.
-   Offline ranking evaluation against synthetic relevance labels.
-   LLM campaign-brief interpretation and recommendation explanation.
-   A React dashboard connected to the FastAPI backend.
-   API endpoints for dashboard summaries, matching, explanations, and
    evaluation summaries.

### Out of scope for the current POC

-   Production-grade data connectors to social platforms or influencer
    marketplaces.
-   Verified live influencer profiles or real campaign performance.
-   A production identity, role-based authorization, or enterprise audit
    implementation.
-   A fully validated production ranking model.
-   A hybrid live-ranking pipeline that combines semantic similarity and
    weighted scores, unless implemented and verified separately.
-   Budget allocation and portfolio optimization across multiple
    influencers.
-   Production-scale security, availability, observability, and
    governance controls.

------------------------------------------------------------------------

## 3. User Journey and Business Process

1.  **Open the dashboard.** The React frontend calls the backend to
    retrieve dashboard summary information.
2.  **Enter a campaign brief.** The user describes the product,
    objective, audience, platform, interests, location, and budget.
3.  **Interpret the brief.** The LLM endpoint extracts structured
    campaign criteria.
4.  **Review the criteria.** The user checks the interpreted fields and
    corrects them if the UI supports editing.
5.  **Select a brand if required.** Brand selection provides the context
    needed for brand-affinity scoring.
6.  **Request recommendations.** The frontend sends campaign criteria to
    the matching endpoint.
7.  **Rank candidates.** The weighted matching engine calculates the
    overall score and component scores.
8.  **Review the shortlist.** The dashboard displays influencer details,
    scores, and component metrics.
9.  **Request an explanation.** The LLM receives campaign and influencer
    evidence and returns a summary, strengths, and considerations.
10. **Evaluate the approach.** The evaluation endpoint exposes
    previously computed offline ranking metrics.

### Process flow

``` mermaid
flowchart TD
    A[User opens InfluenceIQ] --> B[Enter campaign brief]
    B --> C[LLM interprets brief]
    C --> D[Structured campaign criteria]
    D --> E[Review criteria and select brand]
    E --> F[Request recommendations]
    F --> G[Load synthetic data]
    G --> H[Weighted matching engine]
    H --> I[Ranked shortlist and score breakdown]
    I --> J[Select influencer]
    J --> K[LLM explanation endpoint]
    K --> L[Summary, strengths and considerations]
    M[Offline ranking evaluation] --> N[Precision@K, Recall@K and NDCG@K]
```

The semantic matcher is currently an independently evaluated matching
approach. The diagram does not imply that semantic similarity is
automatically fused into the live recommendation score.

------------------------------------------------------------------------

## 4. Solution Architecture

### Logical components

  -----------------------------------------------------------------------
  Component               Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  User interface          React, TypeScript, Vite Campaign entry,
                                                  dashboard,
                                                  recommendations and
                                                  explanations

  API layer               FastAPI                 HTTP endpoints, request
                                                  validation and
                                                  coordination

  Campaign interpretation LLM integration         Convert
                                                  natural-language briefs
                                                  into structured
                                                  criteria

  Weighted matcher        Python                  Calculate match score
                                                  and component scores

  Semantic matcher        Sentence Transformers   Semantic matching and
                                                  ranking experiments

  Explanation service     LLM integration         Explain a
                                                  recommendation using
                                                  supplied evidence

  Synthetic data          Python                  Create development
  generator                                       datasets

  Data files              CSV and Parquet         Store synthetic
                                                  entities and
                                                  performance records

  Evaluation module       Python                  Calculate ranking
                                                  metrics and summaries
  -----------------------------------------------------------------------

### Architecture diagram

``` mermaid
flowchart LR
    U[Campaign planner] --> UI[React + TypeScript dashboard]
    UI --> API[FastAPI]
    API --> BRIEF[Campaign interpretation]
    API --> MATCH[Weighted matching engine]
    API --> EXPLAIN[Recommendation explanation]
    API --> SUMMARY[Dashboard and evaluation APIs]
    BRIEF --> LLM[Configured LLM provider]
    EXPLAIN --> LLM
    MATCH --> DATA[(Synthetic CSV / Parquet)]
    SEM[Semantic matcher] --> EVAL[Ranking evaluation]
    MATCH --> EVAL
    DATA --> EVAL
    API --> UI
```

### Architectural observations

-   The frontend and backend are independently runnable applications.
-   FastAPI separates UI behavior from backend business logic.
-   The weighted engine and semantic matcher have different purposes and
    should be evaluated separately unless an explicit fusion strategy is
    implemented.
-   Synthetic data enables repeatable testing without live external
    data.
-   LLM output supports interpretation and explanation; the structured
    matching engine should remain the source of numerical ranking
    scores.

------------------------------------------------------------------------

## 5. Technology Stack

### Frontend

-   React
-   TypeScript
-   Vite
-   Browser-based HTTP calls to the FastAPI backend

Principal frontend files include `frontend/src/App.tsx` and
`frontend/src/services/api.ts`. The API service uses
`http://localhost:8000` as its default backend base URL.

### Backend

-   Python
-   FastAPI
-   Uvicorn
-   Pydantic request schemas
-   Sentence Transformers for semantic matching
-   An LLM provider configured through environment variables

### Data and evaluation

-   CSV for inspectable tabular data
-   Parquet for columnar storage
-   Synthetic relevance labels for offline evaluation
-   Precision@K, Recall@K, and NDCG@K for ranking evaluation

Exact package versions should be taken from the repository's dependency
files. This README does not prescribe versions that have not been
verified from those files.

------------------------------------------------------------------------

## 6. Repository Structure

The following is a guide to the principal files discussed during
development. Some files or folders may be absent or named differently in
the current checkout; use the actual repository tree as the source of
truth.

``` text
influencer-matching/
├── backend/
│   └── app/
│       ├── api/
│       │   ├── dashboard_routes.py
│       │   ├── llm_routes.py
│       │   ├── matching_routes.py
│       │   └── evaluation_routes.py
│       ├── data_generation/
│       │   └── generator.py
│       ├── matching/
│       │   └── engine.py
│       ├── ml/
│       │   ├── semantic_matcher.py
│       │   └── evaluation.py
│       ├── llm/
│       │   └── schemas.py
│       └── main.py
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── App.tsx
│   ├── package.json
│   └── ...
├── data/
│   ├── synthetic/
│   └── output/
├── tests/
├── .gitignore
└── README.md
```

### Important backend modules

-   `backend/app/main.py`: FastAPI setup and router registration.
-   `backend/app/api/dashboard_routes.py`: dashboard summary endpoint.
-   `backend/app/api/llm_routes.py`: campaign interpretation and
    recommendation explanation endpoints.
-   `backend/app/api/matching_routes.py`: brand and influencer matching
    endpoints.
-   `backend/app/api/evaluation_routes.py`: ranking evaluation summary
    endpoint.
-   `backend/app/data_generation/generator.py`: synthetic data creation.
-   `backend/app/matching/engine.py`: weighted matching and score
    breakdown.
-   `backend/app/ml/semantic_matcher.py`: semantic matching
    implementation.
-   `backend/app/ml/evaluation.py`: ranking evaluation functions.
-   `backend/app/llm/schemas.py`: structured request/response models.
-   `frontend/src/services/api.ts`: frontend API client.
-   `frontend/src/App.tsx`: primary dashboard interface.

------------------------------------------------------------------------

## 7. Synthetic Data Model

The generator creates a synthetic influencer-marketing ecosystem. The
records support local testing and demonstrations; they are not real
people or verified campaign records.

### Reported generation scale

  ------------------------------------------------------------------------
  Dataset                   Approximate record count Purpose
  --------------------- ---------------------------- ---------------------
  Influencers                                  5,000 Influencer profile
                                                     and rate information

  Audience segments                           15,000 Audience
                                                     demographics,
                                                     location and
                                                     interests

  Brands                                         100 Brand entities

  Products                                       500 Products associated
                                                     with brands

  Brand affinity                              10,000 Influencer-to-brand
                                                     affinity evidence

  Campaigns                                    2,000 Campaign definitions

  Campaign performance                        10,000 Synthetic campaign
                                                     outcomes and
                                                     relevance labels
  ------------------------------------------------------------------------

These are previously reported generator settings. Confirm actual output
row counts after regeneration.

### Main entities and fields

#### Influencers

Typical fields: `influencer_id`, `display_name`, `platform`,
`primary_niche`, `follower_count`, `engagement_rate`, `location`,
`average_rate`, `verified`.

#### Audience segments

Typical fields: `audience_segment_id`, `influencer_id`, `age_min`,
`age_max`, `gender`, `location`, `interests`, `audience_share`.

The `interests` field is stored as a JSON string in generated CSV data.
Confirm whether `audience_share` values are normalized per influencer
before using them as a strict probability distribution.

#### Brands and products

Brand records identify the entities associated with products and
campaigns. Product records provide product-level context.

#### Brand affinity

Typical fields: `influencer_id`, `brand_id`, `category_match`,
`affinity_score`.

#### Campaigns

Typical fields: `campaign_id`, `brand_id`, `product_id`, `objective`,
`platform`, `target_category`, `target_age_min`, `target_age_max`,
`target_location`, `target_interests`, `budget`.

#### Campaign performance

Performance records include campaign/influencer outcomes and synthetic
relevance fields such as `synthetic_relevance_score` and `is_relevant`.

### Conceptual relationships

``` mermaid
erDiagram
    BRAND ||--o{ PRODUCT : owns
    BRAND ||--o{ CAMPAIGN : sponsors
    PRODUCT ||--o{ CAMPAIGN : promotes
    INFLUENCER ||--o{ AUDIENCE_SEGMENT : has
    INFLUENCER ||--o{ BRAND_AFFINITY : has
    BRAND ||--o{ BRAND_AFFINITY : receives
    INFLUENCER ||--o{ CAMPAIGN_PERFORMANCE : participates
    CAMPAIGN ||--o{ CAMPAIGN_PERFORMANCE : records
```

This is a conceptual model. Verify exact join keys and cardinalities
against the generated data before treating it as a formal relational
schema.

------------------------------------------------------------------------

## 8. Data Generation and Reproducibility

The generator is located at `backend/app/data_generation/generator.py`
and produces CSV and Parquet outputs under `data/synthetic/`.

From the repository root, activate the development environment:

``` powershell
cd D:\Hackathon\influencer-matching\influencer-matching
.\.venv313\Scripts\Activate.ps1
```

Inspect the generator's entry point before running it:

``` powershell
Get-Content .\backend\app\data_generation\generator.py
```

Use the documented invocation if one exists. If the file has no CLI
entry point, call its public function from a small Python script after
checking its signature. Do not assume a module invocation that the
source does not support.

### Data-quality checks

-   Expected output files exist.
-   Required columns are present.
-   IDs are unique where expected.
-   Entity identifiers refer to existing entities.
-   Numeric values are within expected ranges.
-   Interest JSON strings parse correctly.
-   Performance data includes required relevance labels.
-   Generated data contains no sensitive imported information.

------------------------------------------------------------------------

## 9. Weighted Matching Engine

The weighted matching engine is implemented in
`backend/app/matching/engine.py`.

Its interface has been described as:

``` python
InfluencerMatchingEngine.match(
    campaign,
    influencers,
    audiences,
    brand_affinity,
    campaign_performance
)
```

The engine returns ranked influencer results with an overall match
score, influencer profile fields, and score components.

### Scoring dimensions

  -----------------------------------------------------------------------
  Dimension                           Intended meaning
  ----------------------------------- -----------------------------------
  Audience fit                        Alignment between target
                                      demographics, location, and
                                      interests and the influencer's
                                      audience

  Engagement quality                  Engagement signal relative to the
                                      candidate's profile

  Brand affinity                      Available affinity evidence between
                                      influencer and selected brand

  Historical performance              Evidence from past campaign
                                      performance records

  Cost effectiveness                  Relative value based on estimated
                                      collaboration cost and campaign
                                      budget
  -----------------------------------------------------------------------

The precise formulas, normalization, fallback values, and weights must
be read from the current `engine.py`; they should not be inferred from
component names alone.

### Conceptual scoring formula

A weighted score commonly has this structure:

\[ S(i,c) = `\sum`{=tex}\_{j=1}\^{m} w_j , s_j(i,c) \]

Here, (i) is an influencer, (c) is the campaign, (s_j) is a normalized
component score, and (w_j) is the corresponding weight. Weights
typically sum to 1 when represented as proportions.

This equation explains the weighted-scoring concept; it is not a
verified copy of the current implementation.

### Matching considerations

1.  **Category mismatch:** A food influencer should not automatically
    rank highly for skincare just because engagement and cost are
    favorable.
2.  **Influencer location vs. audience location:** An influencer based
    in Canada may still reach a relevant Indian audience. These are
    separate signals.
3.  **Missing evidence:** A neutral default must be distinguishable from
    a measured score. Missing historical performance is not proof of
    average performance.
4.  **Cost normalization:** Very high cost-effectiveness scores should
    be checked against the price distribution and formula.
5.  **Hard filters vs. soft scores:** Decide whether platform, location,
    category, and budget are mandatory filters or ranking signals.
6.  **Budget semantics:** The current workflow has treated budget as a
    maximum acceptable individual influencer fee. It does not
    demonstrate total-budget allocation across a portfolio.
7.  **Score comparability:** Component scores should use consistent
    scales and documented transformations.
8.  **Determinism:** Identical data and criteria should produce the same
    ranking unless randomness is intentionally part of the design.

### Observed test behavior

During dashboard testing, two recommendations had overall scores around
59.5 and 59.23 despite different location and niche characteristics. One
was a Canada-based lifestyle influencer; another was an India-based food
influencer for a skincare campaign.

The explanations identified these mismatches. This demonstrates that the
explanation step can surface concerns, but it also indicates that the
scoring formula and component contributions should be inspected before
the ranking is considered production-ready.

------------------------------------------------------------------------

## 10. Semantic Matching

The semantic matching implementation is located in
`backend/app/ml/semantic_matcher.py` and uses Sentence Transformers to
create semantic representations for matching.

Semantic representations may help compare meaning instead of relying
only on exact string equality---for example, "skin health" and
"skincare," or related wellness interests.

### Design distinction

The project has a weighted baseline and a semantic matching
implementation with offline evaluation. The live recommendation endpoint
has been reported to use the weighted engine; offline semantic metrics
do not prove that semantic similarity is included in live ranking.

A possible future hybrid design is:

\[ S\_{`\text{hybrid}`{=tex}} =
`\alpha `{=tex}S\_{`\text{weighted}`{=tex}} +
(1-`\alpha`{=tex})S\_{`\text{semantic}`{=tex}} \]

This is a proposed design option, not a description of the current code.
Implement it only after defining score calibration, eligibility rules,
weights, and evaluation criteria.

------------------------------------------------------------------------

## 11. LLM Campaign Interpretation

LLM request schemas are located in `backend/app/llm/schemas.py`. The
campaign-interpretation request uses a natural-language `brief` field.

The structured criteria model includes:

-   Objective: Awareness, Engagement, Conversions, or Sales
-   Platform: Instagram, YouTube, or TikTok
-   Target category from a defined list
-   Minimum and maximum target age
-   Target location
-   Target interests
-   Positive numeric budget

### Interpretation workflow

1.  The user enters a free-text brief.
2.  The backend calls the configured LLM integration.
3.  The model extracts structured fields.
4.  The response is validated against the schema.
5.  The frontend displays the interpreted criteria.
6.  The user reviews them before requesting a ranking.

### Validation considerations

-   Verify the chosen category matches the brief.
-   Check that age ranges are valid and ordered.
-   Confirm that the budget is numeric and positive.
-   Ensure the platform is supported.
-   Clarify ambiguous currency, budget scope, or location.
-   Ask for missing critical criteria rather than silently inventing
    them.
-   Treat generated criteria as a proposal that must pass schema
    validation.

------------------------------------------------------------------------

## 12. AI Recommendation Explanation

The explanation endpoint accepts campaign information, influencer
evidence, and score breakdown. It returns a structured explanation
containing an influencer identifier, summary, strengths, and
considerations.

Example response shape:

``` json
{
  "influencer_id": "IN003728",
  "summary": "The influencer has a moderate match for the campaign, with relevant strengths and potential gaps.",
  "strengths": [
    "Engagement rate is a positive signal.",
    "The influencer's location aligns with the target market."
  ],
  "considerations": [
    "The primary niche may not align with the target category.",
    "Audience fit should be reviewed."
  ]
}
```

This is an illustrative structure based on the response shape observed
during testing, not a guaranteed literal response for every request.

### Explanation quality principles

-   Ground claims in supplied evidence.
-   Distinguish influencer location from audience geography.
-   Do not describe neutral defaults as verified success.
-   Do not invent demographics, prior campaign results, or brand
    relationships.
-   Explain positive signals and mismatches.
-   Keep numerical scores generated by the matching engine separate from
    LLM-generated prose.
-   Treat explanations as decision support, not proof that a
    recommendation is correct.

------------------------------------------------------------------------

## 13. Ranking Evaluation

The evaluation functions are in `backend/app/ml/evaluation.py`. The
project reports Precision@K, Recall@K, and NDCG@K.

### Precision@K

The proportion of the top (K) results labeled relevant.

\[ `\operatorname{Precision@K}`{=tex} =
`\frac{\text{Relevant items in top }K}{K}`{=tex} \]

### Recall@K

The proportion of all relevant items retrieved in the top (K).

\[ `\operatorname{Recall@K}`{=tex} =
`\frac{\text{Relevant items in top }K}{\text{Total relevant items}}`{=tex}
\]

### NDCG@K

Normalized Discounted Cumulative Gain rewards relevant items that appear
higher in the ranking and normalizes against an ideal ordering.

### Previously reported results

  Metric @ 10      Semantic matching   Weighted baseline
  -------------- ------------------- -------------------
  Precision@10                 0.80%               0.40%
  Recall@10                    2.23%               1.25%
  NDCG@10                      2.46%               0.52%

These results were reported from the generated evaluation artifacts
during development. Re-run evaluation and inspect
`ranking_evaluation_summary.csv` and `ranking_evaluation.json` before
using the figures in a formal presentation.

### Interpretation

-   The reported semantic approach scores higher than the weighted
    baseline on all three metrics.
-   Absolute values are low, so neither approach should be presented as
    high-performing without further investigation.
-   Labels are synthetic and reflect generator assumptions.
-   Results depend on relevance generation, candidate sampling, and
    evaluation-set construction.
-   Verify metric implementation, cutoff (K), denominator behavior, and
    relevance definition.

### Recommended evaluation improvements

1.  Use a fixed, documented evaluation split.
2.  Avoid leakage between relevance-label generation and model features.
3.  Report results at multiple cutoffs, such as 5, 10, and 20.
4.  Compare weighted, semantic, and hybrid ranking on the same
    candidates and labels.
5.  Analyze slices by category, platform, audience location, and budget.
6.  Inspect failure cases, not only aggregate metrics.
7.  Validate against human judgments or real campaign outcomes before
    claiming business impact.

------------------------------------------------------------------------

## 14. API Reference

The backend is served by FastAPI. Open Swagger UI at:

``` text
http://localhost:8000/docs
```

### Known endpoints

  -----------------------------------------------------------------------------------
  Method                  Endpoint                            Purpose
  ----------------------- ----------------------------------- -----------------------
  GET                     `/health`                           Basic backend health
                                                              check

  GET                     `/api/dashboard/summary`            Dashboard counts and
                                                              data-source indicator

  POST                    `/api/llm/interpret-campaign`       Interpret a
                                                              natural-language
                                                              campaign brief

  POST                    `/api/llm/explain-recommendation`   Explain a selected
                                                              recommendation

  GET                     `/api/matching/brands`              Return available brands

  POST                    `/api/matching/recommendations`     Return ranked
                                                              influencer
                                                              recommendations

  POST                    `/api/matching/explain`             Matching-related
                                                              explanation route, if
                                                              registered

  GET                     `/api/evaluation/summary`           Return ranking
                                                              evaluation summary
  -----------------------------------------------------------------------------------

Confirm exact paths, methods, and request bodies in the current router
source and `/docs`. The matching explanation route and LLM explanation
route may have different purposes or request contracts.

### Dashboard summary

The previously observed response included:

``` json
{
  "influencers_indexed": 5000,
  "campaigns_analyzed": 2000,
  "data_source": "synthetic"
}
```

The counts depend on generated files and the current backend
implementation.

### Basic API checks

``` powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/api/dashboard/summary
```

For POST requests, use the exact schema displayed in Swagger UI or the
frontend API client.

------------------------------------------------------------------------

## 15. Local Development Setup

These instructions reflect the Windows PowerShell environment used
during development. Verify the repository's dependency files before
installing packages.

### Prerequisites

-   Git
-   A Python version compatible with project dependencies
-   Node.js and npm
-   An LLM API key for LLM workflows
-   Disk space for ML dependencies and generated data

Python 3.13 was used in the described development environment. If a
dependency does not support that version, use a compatible version
specified by the repository.

### Clone the repository

``` powershell
git clone https://github.com/dibseal/influencer-matching.git
cd influencer-matching
```

### Create and activate a virtual environment

``` powershell
py -3.13 -m venv .venv313
.\.venv313\Scripts\Activate.ps1
python --version
```

You can also invoke the environment's Python directly:

``` powershell
.\.venv313\Scripts\python.exe --version
```

### Install backend dependencies

Inspect available dependency files:

``` powershell
Get-ChildItem -Name requirements*.txt, pyproject.toml
```

If a root `requirements.txt` exists:

``` powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If dependencies are stored elsewhere, use the correct path. Do not
assume a requirements file exists until you have checked.

### Configure environment variables

Create the local `.env` file where the backend configuration expects it.
During development, an environment file under `backend/.env` was used;
verify the current settings code for the exact location and variable
names.

Example template:

``` dotenv
OPENAI_API_KEY=replace_with_your_local_key
OPENAI_MODEL=gpt-4o-mini
```

Use the exact variable names expected by the current application. Never
commit `.env` or share API keys in logs, presentations, or chat. If a
key has been exposed, revoke it and create a replacement.

### Start the backend

From the repository root:

``` powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Or explicitly use the virtual environment:

``` powershell
.\.venv313\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

The API should be available at `http://localhost:8000`. Keep this
terminal open.

### Start the frontend

Open a second PowerShell terminal:

``` powershell
cd frontend
npm install
npm run dev
```

Vite normally prints a URL such as `http://localhost:5173`. Use the
actual URL it displays.

### CORS

The backend configuration used during development allowed
`http://localhost:5173`. If Vite uses a different port, update the
backend CORS configuration deliberately rather than disabling CORS
globally.

------------------------------------------------------------------------

## 16. End-to-End Test Procedure

### Test 1 --- Service availability

1.  Start the backend.
2.  Start the frontend.
3.  Open `http://localhost:5173`.
4.  Open `http://localhost:8000/health`.
5.  Open `http://localhost:8000/docs`.

**Expected:** UI loads and the API is reachable.

### Test 2 --- Dashboard summary

Verify that the dashboard displays generated data counts. During
development, expected values were 5,000 influencers and 2,000 campaigns.

**Expected:** counts are returned by the backend and shown in the UI.

### Test 3 --- Campaign interpretation

Use a representative brief:

> We are launching a premium skincare product in India. The objective is
> brand awareness, with engagement as a secondary objective. Target men
> and women aged 25 to 35 in India who are interested in skincare,
> beauty, and wellness. Use Instagram influencers with relevant
> audiences, strong engagement, positive historical performance, and
> good brand affinity. The campaign budget is ₹500,000. Recommend
> suitable influencers and explain their strengths and potential risks.

Verify the interpreted objective, platform, category, age range,
location, interests, and budget. Correct values if the interface permits
editing.

**Expected:** schema-valid campaign criteria.

### Test 4 --- Matching and ranking

1.  Select a brand if requested.
2.  Request recommendations.
3.  Verify that the list is populated and ordered by the displayed
    score.
4.  Review influencer details and score components.
5.  Check that hard eligibility requirements are applied if implemented
    as filters.

**Expected:** ranked results with a score breakdown.

### Test 5 --- Explanation

Select a recommended influencer and request an AI explanation.

**Expected:** a summary, strengths, and considerations consistent with
the supplied evidence.

### Test 6 --- Evaluation summary

``` powershell
Invoke-RestMethod http://localhost:8000/api/evaluation/summary
```

**Expected:** an evaluation summary if the route is registered and its
input artifacts are available.

### Test 7 --- Negative and boundary cases

Test empty briefs, unsupported categories, invalid age ranges, missing
brand selection, non-positive budgets, missing data files, no
candidates, LLM timeouts, invalid LLM output, and unknown influencer
IDs.

**Expected:** meaningful validation errors or graceful handling rather
than an unhandled server crash.

### Test 8 --- Ranking sanity

For an India-focused skincare campaign, inspect why unrelated niches or
other locations appear near the top. Distinguish influencer location
from audience geography. Verify that cost-effectiveness and default
component scores do not overwhelm relevance.

------------------------------------------------------------------------

## 17. Test Results and Known Observations

The following behaviors were observed during manual dashboard testing:

-   The dashboard loaded and displayed API-backed counts.
-   Ranked recommendations appeared with overall scores and component
    breakdowns.
-   The recommendation-explanation action returned structured JSON with
    an influencer ID, summary, strengths, and considerations.
-   Explanations identified potential niche and location mismatches.
-   Two example influencers received similar scores (approximately 59.50
    and 59.23) despite different niche/location profiles.
-   Cost-effectiveness scores were close to 100/100 for both examples.
-   Brand-affinity and historical-performance components were displayed
    as 50/100 in the reviewed examples.

These observations warrant checking the matching formula and fallback
behavior. They do not alone prove a defect; inspect the actual component
formulas and weights.

------------------------------------------------------------------------

## 18. Security and Repository Hygiene

### Never commit

-   `.env` files or API keys
-   Python virtual environments (`.venv`, `.venv313`, `venv`)
-   Python bytecode and `__pycache__` directories
-   Frontend `node_modules`
-   Regenerable build output
-   Large binary dependency files from installed packages

Suggested `.gitignore` entries:

``` gitignore
# Secrets
.env
.env.*
!.env.example

# Python environments
.venv/
.venv*/
venv/
env/

# Python cache
__pycache__/
*.py[cod]

# Frontend dependencies and build output
frontend/node_modules/
frontend/dist/
```

Synthetic CSV/Parquet files may be committed if reasonably sized and
free of sensitive data. GitHub rejects individual ordinary Git files
over 100 MB. If a large file is already in unpublished history,
`.gitignore` alone does not remove it from that history.

### API security considerations for future deployment

-   Keep provider keys on the backend, never in frontend bundles.
-   Validate request bodies and enforce payload-size limits.
-   Add authentication and authorization before exposing enterprise or
    private data.
-   Rate-limit LLM-backed endpoints and set sensible timeouts.
-   Avoid logging secrets or unnecessary personal data.
-   Treat user-provided briefs and retrieved content as untrusted input.
-   Ground generated explanations in server-provided evidence.

------------------------------------------------------------------------

## 19. Performance, Reliability, and Observability

The current project is a proof of concept. Measure rather than assume:

-   API latency for campaign interpretation and matching
-   LLM latency and failure rate
-   Data loading and preprocessing time
-   Ranking latency as the candidate set grows
-   Memory consumption for semantic embeddings
-   Error rates for invalid briefs and missing data
-   Repeatability of scores across identical requests

Potential future improvements include caching precomputed embeddings,
caching frequently used datasets, avoiding repeated full-file reads per
request, and adding structured logs and request correlation IDs. These
are recommendations, not claims that the optimizations are already
implemented.

------------------------------------------------------------------------

## 20. Current Limitations and Risks

1.  **Synthetic data:** Profiles, audience segments, affinities, and
    performance outcomes are generated, not verified.
2.  **Synthetic labels:** Offline metrics measure agreement with
    generated relevance assumptions, not proven campaign success.
3.  **Low reported evaluation metrics:** The recorded top-10 metrics are
    low in absolute terms and require investigation.
4.  **Separate semantic and live ranking paths:** Offline semantic
    evaluation does not mean semantic similarity is used in live
    recommendations.
5.  **Score calibration:** Similar overall scores and very high
    cost-effectiveness scores warrant review.
6.  **Audience geography:** Influencer location and audience location
    must not be conflated.
7.  **Missing evidence:** Neutral defaults need explicit missing-data
    indicators.
8.  **Budget meaning:** A per-influencer fee limit is not equivalent to
    a campaign-wide portfolio budget.
9.  **LLM reliability:** Interpretation and explanation outputs can be
    incomplete or inaccurate and require validation.
10. **Production controls:** Authentication, authorization,
    auditability, monitoring, and deployment hardening need separate
    assessment.

------------------------------------------------------------------------

## 21. Recommended Next Steps

### Priority 1 --- Validate ranking correctness

-   Inspect exact weights and normalization in `engine.py`.
-   Review category relevance and audience-location calculations.
-   Identify missing-data defaults and expose them explicitly.
-   Test cost effectiveness against the distribution of `average_rate`.
-   Add unit tests for expected ranking behavior and boundary
    conditions.

### Priority 2 --- Improve evaluation quality

-   Re-run metrics and verify evaluation artifacts.
-   Document synthetic relevance generation.
-   Investigate low reported metrics.
-   Evaluate ranking slices by category, platform, audience location,
    and budget.
-   Establish human-reviewed relevance labels before claiming real-world
    value.

### Priority 3 --- Decide on semantic/hybrid ranking

-   Keep the weighted baseline as a transparent benchmark.
-   Calibrate semantic similarity scores.
-   Test a hybrid score on the same held-out candidates and labels.
-   Compare quality, latency, and explainability before selecting a
    default.

### Priority 4 --- Improve campaign planning

-   Clarify whether budget is a per-influencer cap or total campaign
    budget.
-   If total budget is required, add portfolio selection under budget
    constraints.
-   Add controls for minimum audience fit, category alignment, and
    market relevance.
-   Display missing evidence and confidence/coverage indicators.

### Priority 5 --- Prepare for deployment

-   Add automated tests to CI.
-   Document environment configuration.
-   Add authentication, authorization, rate limits, and observability.
-   Define data retention and governance rules.
-   Deploy frontend and backend with managed secrets and monitored
    health checks.

------------------------------------------------------------------------

## 22. Presentation Storyline

This README is structured to support a later PowerPoint presentation. A
suggested storyline:

1.  **Business challenge:** influencer selection is multi-dimensional
    and difficult to compare consistently.
2.  **Solution vision:** InfluenceIQ translates a natural-language brief
    into a ranked, explainable shortlist.
3.  **User journey:** brief → structured criteria → matching → ranked
    candidates → explanation.
4.  **Architecture:** React, FastAPI, weighted matching, semantic
    matching, LLM services, synthetic data.
5.  **Data foundation:** synthetic entities, audience segments, brand
    affinities, and campaign outcomes.
6.  **Matching approach:** five scoring dimensions and the distinction
    between filters and ranking.
7.  **Generative AI:** campaign interpretation and evidence-grounded
    explanations.
8.  **Evaluation:** Precision@10, Recall@10, and NDCG@10, with
    synthetic-data caveats.
9.  **Demo results:** dashboard recommendations and explanations from
    manual testing.
10. **Lessons learned:** ranking relevance, score calibration, location
    semantics, and missing-data handling.
11. **Roadmap:** improve ranking and evaluation, test hybrid ranking,
    add portfolio budget optimization, and harden deployment.
12. **Conclusion:** demonstrate end-to-end capability while
    distinguishing POC behavior from production readiness.

### Suggested presentation message

> InfluenceIQ demonstrates an end-to-end approach to influencer
> discovery: interpret a campaign brief, rank candidates using explicit
> scoring dimensions, and explain the strengths and limitations of
> individual recommendations. The current POC establishes the workflow
> and evaluation foundation; further validation against human judgments
> and real campaign outcomes is required before production decisions.

------------------------------------------------------------------------

## 23. Glossary

  -----------------------------------------------------------------------
  Term                                Meaning
  ----------------------------------- -----------------------------------
  Campaign brief                      Natural-language description of the
                                      marketing goal and target audience

  Structured criteria                 Validated fields extracted from the
                                      brief

  Weighted matching                   Ranking based on a weighted
                                      combination of component scores

  Semantic matching                   Matching based on semantic
                                      representations rather than exact
                                      string overlap alone

  Audience fit                        Alignment between campaign target
                                      and influencer audience

  Brand affinity                      Available evidence of fit between
                                      an influencer and a brand

  Precision@K                         Relevant proportion among the top K
                                      ranked results

  Recall@K                            Proportion of all relevant results
                                      retrieved in the top K

  NDCG@K                              Ranking metric that rewards
                                      relevant results near the top

  Synthetic data                      Artificially generated data used
                                      for development and controlled
                                      testing

  LLM                                 Large language model used for
                                      language interpretation and
                                      explanation
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 24. Final Status

InfluenceIQ is a working proof of concept demonstrating a full-stack
influencer-matching workflow with synthetic data, a weighted matching
engine, a semantic matching experiment, LLM-based campaign
interpretation, and recommendation explanations.

The dashboard and explanation workflow have been manually exercised. The
next engineering priority is to validate the exact matching formulas and
synthetic evaluation methodology, improve ranking relevance, and
distinguish measured evidence from defaults or generated assumptions.

**Before using this README as a definitive technical specification,
reconcile file names, endpoint contracts, dependency instructions,
generator commands, and score formulas against the current repository
source.** Where implementation details have not been verified, this
document describes them as conceptual or to be confirmed.
