from fastapi import FastAPI

from api.routes import router as api_router

app = FastAPI(title="Medical Guidance Orchestrator API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


app.include_router(api_router)
