from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.request
import urllib.parse
import json
import os

app = FastAPI(title="Radamn Engine Core", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatPayload(BaseModel):
    user_id: str = "default_user"
    message: str
    image_url: str = None

# A SUA CHAVE DA SUA API
RADAMN_API_KEY = os.getenv("RADAMN_API_KEY")

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn Engine Core v2.0",
        "auth_enabled": bool(RADAMN_API_KEY)
    }

@app.post("/api/chat")
async def process_chat(payload: ChatPayload, authorization: str = Header(None)):
    # Validação da sua própria chave
    if RADAMN_API_KEY:
        expected_token = f"Bearer {RADAMN_API_KEY}"
        if authorization != expected_token and authorization != RADAMN_API_KEY:
            raise HTTPException(status_code=401, detail="Chave de API do Radamn inválida ou não fornecida.")

    prompt = payload.message.strip()

    # 1. Geração de Imagem HD (Flux Engine)
    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Sua imagem HD foi gerada pelo motor Radamn Engine!",
            "media_url": img_url
        }

    # 2. Resposta do Motor Radamn Engine
    return {
        "status": "success",
        "type": "text",
        "response": f"Radamn Engine: Processado com sucesso sob autorização da sua chave própria!"
    }
    
