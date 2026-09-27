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

    # 2. Suporte a Prompt de Texto
    full_prompt = prompt
    if payload.image_url:
        full_prompt = f"[Imagem para análise: {payload.image_url}]\nPergunta: {prompt}"

    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    # URL atualizado da Router API do Hugging Face
    endpoints = [
        f"https://router.huggingface.co/hf-inference/v1/models/{MODEL_NAME}",
        f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
    ]

    response_data = None
    last_error = None

    for url in endpoints:
        try:
            hf_response = requests.post(
                url,
                headers=headers,
                json={"inputs": full_prompt},
                timeout=25
            )
            if hf_response.status_code == 200:
                response_data = hf_response.json()
                break
            else:
                last_error = f"Status {hf_response.status_code}: {hf_response.text}"
        except Exception as err:
            last_error = str(err)

    if not response_data:
        return {
            "status": "error",
            "type": "text",
            "response": f"⚠️ Não foi possível comunicar com o modelo no Hugging Face. Detalhes: {last_error}"
        }

    reply = ""
    if isinstance(response_data, list) and len(response_data) > 0:
        item = response_data[0]
        if isinstance(item, dict):
            reply = item.get("generated_text") or item.get("summary_text") or str(item)
        else:
            reply = str(item)
    elif isinstance(response_data, dict):
        if "generated_text" in response_data:
            reply = response_data["generated_text"]
        elif "error" in response_data:
            reply = f"⚠️ Aviso do Modelo: {response_data['error']}"
        else:
            reply = str(response_data)

    if reply.startswith(full_prompt):
        reply = reply[len(full_prompt):].strip()

    if not reply:
        reply = "Recebi sua mensagem, mas não consegui gerar uma resposta em texto."

    return {
        "status": "success",
        "type": "text",
        "response": reply
    }
    
