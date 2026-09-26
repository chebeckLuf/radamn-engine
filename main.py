from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="Radamn Engine Core", version="2.0")

# Libera o acesso para qualquer interface (Web, App, etc.)
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

MODEL_NAME = "LuffyNox/radamn-ai-v1"

@app.get("/")
def status():
    return {"status": "Online", "engine": "Radamn AI Core v2.0", "limit_cpu": False}

@app.post("/api/chat")
async def process_chat(payload: ChatPayload):
    prompt = payload.message.strip()
    
    # 1. Comando de Geração de Imagem HD (Flux)
    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = requests.utils.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Sua imagem HD foi gerada pelo motor Radamn!",
            "media_url": img_url
        }

    # 2. Suporte à Visão Multimodal
    full_prompt = prompt
    if payload.image_url:
        full_prompt = f"[Imagem para análise: {payload.image_url}]\nPergunta: {prompt}"

    # 3. Chamada ao Modelo LuffyNox
    try:
        hf_response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
            json={"inputs": full_prompt},
            timeout=30
        )
        data = hf_response.json()
        
        reply = ""
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            reply = data[0]["generated_text"]
        elif isinstance(data, dict) and "generated_text" in data:
            reply = data["generated_text"]
        elif isinstance(data, dict) and "error" in data:
            reply = f"⚠️ Aviso do Modelo: {data['error']}"
        else:
            reply = "Mensagem processada pelo motor Radamn AI."

        return {
            "status": "success",
            "type": "text",
            "response": reply
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
      
