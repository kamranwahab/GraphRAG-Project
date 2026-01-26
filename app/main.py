from fastapi import FastAPI
from pydantic import BaseModel
from app.services.rag_orchestrator import RAGOrchestrator

app = FastAPI()
rag = RAGOrchestrator()

class ChatRequest(BaseModel):
    message: str
    api_url: str

@app.post("/ingest")
def ingest():
    return {"status": rag.ingest("data/raw/UET_Prospectus.pdf")}

@app.post("/chat")
def chat(req: ChatRequest):
    return {"response": rag.query(req.message, req.api_url)}