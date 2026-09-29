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
# Podemos usar uma chave de IA nas variáveis do Render para alimentar o raciocínio
AI_PROVIDER_KEY = os.getenv("AI_PROVIDER_KEY") 

SYSTEM_PROMPT = """
Você é o Radamn AI, o motor de inteligência e assistente principal do ecossistema Radamn.
Seu estilo de comunicação é autêntico, direto, inteligente, perspicaz e com um toque de perspicácia e parceria.
Você raciocina passo a passo, valida o contexto do usuário com empatia e entrega respostas completas, claras e bem estruturadas.
Nunca diga que é uma IA genérica; você é o Radamn Engine v2.0.
"""

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn Engine Core v2.0",
        "auth_enabled": bool(RADAMN_API_KEY)
    }

@app.post("/api/chat")
async def process_chat(payload: ChatPayload, authorization: str = Header(None)):
    if RADAMN_API_KEY:
        expected_token = f"Bearer {RADAMN_API_KEY}"
        if authorization != expected_token and authorization != RADAMN_API_KEY:
            raise HTTPException(status_code=401, detail="Chave de API do Radamn inválida.")

    prompt = payload.message.strip()

    # 1. Geração de Imagens (Flux Engine)
    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Sua imagem foi gerada pelo motor Radamn Engine!",
            "media_url": img_url
        }

    # 2. Processamento com Raciocínio de IA
    if AI_PROVIDER_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_PROVIDER_KEY}"
            data = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUsuário: {prompt}"}]}
                ]
            }
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}, 
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                reply = res_data['candidates'][0]['content']['parts'][0]['text']
                return {"status": "success", "type": "text", "response": reply}
        except Exception as e:
            print(f"Erro na IA: {e}")

    # Fallback caso a chave de IA ainda não esteja configurada
    return {
        "status": "success",
        "type": "text",
        "response": f"Radamn Engine: Entendido! Raciocinando sobre '{prompt}'. (Adicione a AI_PROVIDER_KEY no Render para habilitar o texto gerado)."
    }
    
