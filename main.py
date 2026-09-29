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

RADAMN_API_KEY = os.getenv("RADAMN_API_KEY")
AVS_URL = os.getenv("AVS_URL")

SYSTEM_PROMPT = """
Você é o Radamn AI, o motor de inteligência e assistente principal do ecossistema Radamn.
Seu estilo de comunicação é autêntico, direto, inteligente, perspicaz e parceiro.
Você raciocina passo a passo e entrega respostas completas e bem estruturadas.
Você é o Radamn Engine v2.0.
"""

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn Engine Core v2.0",
        "auth_enabled": bool(RADAMN_API_KEY),
        "custom_engine_connected": bool(AVS_URL)
    }

@app.post("/api/chat")
async def process_chat(payload: ChatPayload, authorization: str = Header(None)):
    if RADAMN_API_KEY:
        expected_token = f"Bearer {RADAMN_API_KEY}"
        if authorization != expected_token and authorization != RADAMN_API_KEY:
            raise HTTPException(status_code=401, detail="Chave de API do Radamn inválida.")

    prompt = payload.message.strip()

    # 1. Geração de Imagens
    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Sua imagem foi gerada pelo motor Radamn Engine!",
            "media_url": img_url
        }

    # 2. Conexão Direta com a Tua IA Própria (AVS_URL)
    if AVS_URL:
        try:
            payload_data = {
                "message": prompt,
                "system_prompt": SYSTEM_PROMPT
            }
            req = urllib.request.Request(
                AVS_URL, 
                data=json.dumps(payload_data).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}, 
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                # Ajusta a chave de resposta de acordo com o retorno do teu servidor (ex: res_data.get("response"))
                reply = res_data.get("response") or res_data.get("reply") or str(res_data)
                return {"status": "success", "type": "text", "response": reply}
        except Exception as e:
            print(f"Erro na conexao com AVS_URL: {e}")

    return {
        "status": "success",
        "type": "text",
        "response": "Radamn Core: Conectado ao backend próprio."
    }
    
