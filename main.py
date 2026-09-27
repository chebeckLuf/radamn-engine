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

    # 2. Chamada direta ao modelo no Hugging Face (Router API)
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    # Endpoint oficial de Router da HF (OpenAI Chat Format)
    url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
    body = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }

    try:
        res = requests.post(url, headers=headers, json=body, timeout=40)
        
        if res.status_code == 200:
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            return {"status": "success", "type": "text", "response": reply}
        
        # Caso o modelo esteja a carregar (503) ou indisponível na HF Router API:
        elif res.status_code in [503, 404]:
            return {
                "status": "success", 
                "type": "text", 
                "response": f"O modelo `{MODEL_NAME}` está a inicializar nos servidores da Hugging Face. Por favor, tenta enviar a mensagem novamente em 20 segundos!"
            }
        else:
            return {
                "status": "error",
                "type": "text",
                "response": f"⚠️ Erro no servidor Hugging Face ({res.status_code}): {res.text}"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "type": "text",
            "response": "⚠️ O modelo demorou para responder. Tente novamente!"
        }
    except Exception as e:
        return {
            "status": "error",
            "type": "text",
            "response": f"⚠️ Erro na requisição: {str(e)}"
        }
        
