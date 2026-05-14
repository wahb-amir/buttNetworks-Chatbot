from fastapi import FastAPI
from app.api.v1.chatbot import router as webhook_router

app = FastAPI(title="RAG Bot")


app.include_router(
    webhook_router, 
    prefix="", 
    tags=["chatbot"]
)

@app.get("/")
async def root():
    return {"status": "online", "message": "RAG Bot Server is running"}

@app.head("/health")
async def health_check():
    return {"status": "healthy"}