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

# URL da tua AVS Própria hospedada no Render
AVS_URL = os.getenv("AVS_URL", "https://radamanthys-core-vjap.onrender.com/predict")

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn AI Core v2.0", 
        "avs_endpoint": AVS_URL
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

    # 2. Chamada direta ao Motor AVS Próprio no Render
    headers = {"Content-Type": "application/json"}
    body = {"text": prompt}

    try:
        res = requests.post(AVS_URL, headers=headers, json=body, timeout=60)
        
        if res.status_code == 200:
            data = res.json()
            # Pega o campo 'response' ou 'message' do retorno da AVS
            reply = data.get("response") or data.get("message") or "Sem resposta do modelo."
            return {"status": "success", "type": "text", "response": reply}
        
        elif res.status_code == 503:
            return {
                "status": "success", 
                "type": "text", 
                "response": "O motor AVS está a inicializar no Render. Por favor, tente novamente em alguns segundos!"
            }
        else:
            return {
                "status": "error",
                "type": "text",
                "response": f"⚠️ Erro no servidor AVS ({res.status_code}): {res.text}"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "type": "text",
            "response": "⚠️ O motor AVS demorou para responder (Timeout). Tente novamente!"
        }
    except Exception as e:
        return {
            "status": "error",
            "type": "text",
            "response": f"⚠️ Erro na requisição interna: {str(e)}"
        }
        
