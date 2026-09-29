from fastapi import FastAPI, Header, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.parse

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

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn Engine Core v2.0"
    }

@app.post("/api/chat")
async def process_chat(payload: ChatPayload, authorization: Optional[str] = Header(None)):
    prompt = payload.message.strip()

    # 1. Geração de Imagens
    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Sua imagem foi gerada com sucesso pelo motor Radamn Engine!",
            "media_url": img_url
        }

    # 2. Resposta Autónoma com a Identidade do Dataset
    resposta_personalizada = f"Fala, mano! Entendi o teu ponto sobre '{prompt}'. O nosso motor próprio está ativo, limpo de barreiras e pronto para rodar sem limites."

    return {
        "status": "success",
        "type": "text",
        "response": resposta_personalizada
    }
    
