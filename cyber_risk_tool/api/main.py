from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Cyber Risk Underwriting Intelligence Tool",
    description="Agentic AI tool for cyber risk assessment.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Cyber Risk Underwriting Intelligence Tool",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
