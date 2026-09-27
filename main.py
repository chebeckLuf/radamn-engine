from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
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

MODEL_NAME = "LuffyNox/radamn-ai-v1"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn AI Core v2.0", 
        "custom_api_active": bool(HF_TOKEN)
    }

@app.post("/api/chat")
async def process_chat(payload: ChatPayload):
    prompt = payload.message.strip()
    
    # 1. Geração de Imagem HD (Flux)
    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = requests.utils.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Sua imagem HD foi gerada pelo motor Radamn!",
            "media_url": img_url
        }

    # 2. Resposta via Router API da Hugging Face (Formato OpenAI / Chat Completions)
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    # Tenta primeiro a Serverless Router API oficial (OpenAI compatible format)
    router_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
    router_payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        res = requests.post(router_url, headers=headers, json=router_payload, timeout=25)
        if res.status_code == 200:
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            return {"status": "success", "type": "text", "response": reply}
    except Exception:
        pass

    # 3. Fallback: Se o modelo específico não estiver carregado na HF Serverless, responde via IA pública rápida
    try:
        poll_url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
        fallback_res = requests.get(poll_url, timeout=15)
        if fallback_res.status_code == 200 and fallback_res.text.strip():
            return {"status": "success", "type": "text", "response": fallback_res.text.strip()}
    except Exception as err:
        return {"status": "error", "type": "text", "response": f"⚠️ Erro ao gerar resposta: {str(err)}"}

    return {"status": "error", "type": "text", "response": "⚠️ Não foi possível obter resposta no momento."}
    
