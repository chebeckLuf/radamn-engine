from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Radamn Dedicated AVS Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7

@app.get("/")
def home():
    return {"status": "online", "message": "Radamn Engine AVS ativo e autónomo no Termux"}

@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    # Extrai a última mensagem do utilizador para dar uma resposta inteligente e local
    user_msg = "Olá!"
    if req.messages:
        user_msg = req.messages[-1].content

    # Resposta simulada de alta fidelidade para o teu modelo radamn-ai-v1
    resposta_ia = f"Olá! Eu sou o radamn-ai-v1, o teu modelo de inteligência artificial a correr localmente no Termux. Recebi a tua mensagem: '{user_msg}'"

    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": resposta_ia
                }
            }
        ]
    }



