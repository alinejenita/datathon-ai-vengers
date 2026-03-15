from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.routes import auth, test_routes, agents

app = FastAPI(
    title="Datathon Backend",
    description="AI Competitive Intelligence Platform for E-commerce Sellers",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(test_routes.router, prefix="/api")
app.include_router(agents.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logging.info("Datathon backend starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Datathon backend shutting down...")

@app.get("/")
def root():
    return {"message": "Datathon backend running"}