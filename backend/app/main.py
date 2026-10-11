from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.llm_routes import router as llm_router
from backend.app.api.dashboard_routes import router as dashboard_router
from backend.app.api.matching_routes import router as matching_router
from backend.app.api.evaluation_routes import router as evaluation_router

app = FastAPI(
    title="Influencer Matching API",
    description="Hybrid ML and LLM influencer recommendation platform",
    version="1.0.0",
)

app.include_router(llm_router)
app.include_router(dashboard_router)
app.include_router(matching_router)
app.include_router(evaluation_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "influencer-matching-api",
    }
