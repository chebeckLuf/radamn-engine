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

    # 2. Suporte à Visão Multimodal
    full_prompt = prompt
    if payload.image_url:
        full_prompt = f"[Imagem para análise: {payload.image_url}]\nPergunta: {prompt}"

    # 3. Chamada ao Modelo LuffyNox
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    try:
        hf_response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
            headers=headers,
            json={"inputs": full_prompt},
            timeout=30
        )
        data = hf_response.json()
        
        reply = ""
        
        # Tratamento robusto para extrair o texto de qualquer formato do HF
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            if isinstance(item, dict):
                reply = item.get("generated_text") or item.get("summary_text") or item.get("translation_text") or str(item)
            else:
                reply = str(item)
        elif isinstance(data, dict):
            if "generated_text" in data:
                reply = data["generated_text"]
            elif "error" in data:
                reply = f"⚠️ Aviso do Modelo: {data['error']}"
            else:
                reply = str(data)
        else:
            reply = str(data)

        # Remove o prompt enviado caso o modelo o repita na resposta
        if reply.startswith(full_prompt):
            reply = reply[len(full_prompt):].strip()

        if not reply:
            reply = "Recebi sua mensagem, mas não consegui gerar uma resposta em texto."

        return {
            "status": "success",
            "type": "text",
            "response": reply
        }

    except Exception as e:
        return {
            "status": "error",
            "type": "text",
            "response": f"⚠️ Erro ao processar resposta: {str(e)}"
        }
        
