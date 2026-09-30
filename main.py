import math
import random
import re
import urllib.parse
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Radamn Engine Core", version="4.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN ADVANCED CONVERSATIONAL ENGINE v4.5
# =====================================================================

class CognitiveMemory:
    """Memória de curto prazo com capacidade de retenção de contexto."""
    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_interaction(self, role: str, text: str):
        self.history.append({"role": role, "text": text})
        if len(self.history) > 10:
            self.history.pop(0)

    def get_last_user_message(() -> Optional[str]:
        for item in reversed(self.history):
            if item["role"] == "user":
                return item["text"]
        return None


class RadamnConversationalEngine:
    def __init__(self):
        self.memory = CognitiveMemory()

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def generate_response(self, user_input: str) -> str:
        clean_input = self._normalize_text(user_input)

        if not clean_input:
            return "Tô por aqui! Pode mandar a sua mensagem."

        # 1. Prioridade Alta: Reconhecimento do Criador / Dono
        if any(w in clean_input for w in ["criador", "meu criador", "sou seu criador", "radamn humano"]):
            response = "Fala, Radamn! Salve pro meu criador. O sistema tá rodando 100% sob o teu comando!"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return response

        # 2. Prioridade Alta: Perguntas sobre o Contexto/Memória ("Entendeu o que eu disse?", etc.)
        if any(w in clean_input for w in ["entendeu", "entendeu o que", "entendeu oque", "disse antes", "falei antes"]):
            last_msg = self.memory.get_last_user_message()
            if last_msg:
                response = f"Entendi sim! Você tinha falado: '{last_msg}'. Tô acompanhando tudo certinho."
            else:
                response = "Tô acompanhando o nosso papo sim! Pode mandar a braba."
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return response

        # 3. Saudações e Diálogo Natural
        if any(w in clean_input for w in ["tudo bem", "tudo bom", "como vai", "como esta", "beleza"]):
            responses = [
                "Comigo tá tudo ótimo! E com você, como estão as coisas?",
                "Tudo excelente por aqui! Como tá sendo o seu dia?",
                "Tranquilidade total! Sempre pronto pra trocar uma ideia."
            ]
            response = random.choice(responses)
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return response

        if any(w in clean_input for w in ["ola", "oi", "fala", "eai", "salve", "boa noite", "bom dia", "boa tarde"]):
            responses = [
                "Fala! Como posso te ajudar agora?",
                "E aí! Prazer te ver por aqui. O que manda?",
                "Salve! Tô por aqui, pode falar."
            ]
            response = random.choice(responses)
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return response

        # 4. Busca de Conhecimento Técnico (Apenas se NÃO for diálogo pessoal)
        if "o que e ia" in clean_input or "explicacao ia" in clean_input or clean_input == "ia":
            response = "Inteligência Artificial é a capacidade de um sistema computacional processar dados e interagir de forma lógica."
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return response

        # 5. Resposta Fluida Genérica
        self.memory.add_interaction("user", user_input)
        responses = [
            "Entendi o teu ponto! Me conta mais sobre isso.",
            "Show de bola. Tô acompanhando o raciocínio, pode continuar!",
            "Maneiro! Como você quer seguir com isso?"
        ]
        response = random.choice(responses)
        self.memory.add_interaction("assistant", response)
        return response


radamn_core = RadamnConversationalEngine()

# =====================================================================
# ROTAS FASTAPI
# =====================================================================

class ChatPayload(BaseModel):
    user_id: str = "default_user"
    message: str
    image_url: Optional[str] = None

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn Engine Core v4.5 (Context-Aware Conversational Engine)"
    }

@app.post("/api/chat")
async def process_chat(payload: ChatPayload, authorization: Optional[str] = Header(None)):
    prompt = payload.message.strip()

    if prompt.lower().startswith("crie uma imagem") or prompt.lower().startswith("gerar imagem"):
        prompt_encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
        return {
            "status": "success",
            "type": "image",
            "response": "Imagem gerada com sucesso pelo motor Radamn!",
            "media_url": img_url
        }

    resposta_ia = radamn_core.generate_response(prompt)

    return {
        "status": "success",
        "type": "text",
        "response": resposta_ia
    }
    
