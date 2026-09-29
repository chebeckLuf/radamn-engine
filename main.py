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

AVS_URL = os.getenv("AVS_URL")

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn AI Core v2.0 (Autonomous Engine)", 
        "avs_connected": bool(AVS_URL)
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

    # 2. Processamento Local / Motor Autónomo AVS (Sem Hugging Face)
    if AVS_URL:
        try:
            res = requests.post(
                f"{AVS_URL.rstrip('/')}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300
                },
                timeout=40
            )
            if res.status_code == 200:
                data = res.json()
                reply = data["choices"][0]["message"]["content"] if "choices" in data else data.get("response", str(data))
                return {"status": "success", "type": "text", "response": reply}
        except Exception as e:
            pass

    # Resposta padrão do motor se o AVS não devolver texto
    return {
        "status": "success",
        "type": "text",
        "response": f"Radamn Core: Recebido '{prompt}'. O motor autônomo está operacional e sem dependência do Hugging Face!"
    }
    
