import math
import random
import re
import urllib.parse
import urllib.request
import json
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Radamn Engine Core", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN ADVANCED CONVERSATIONAL & SEARCH ENGINE v5.0
# =====================================================================

class CognitiveMemory:
    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_interaction(self, role: str, text: str):
        self.history.append({"role": role, "text": text})
        if len(self.history) > 10:
            self.history.pop(0)

    def get_last_user_message(self) -> Optional[str]:
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

    def search_web(self, query: str) -> str:
        """Realiza busca em tempo real na internet utilizando DuckDuckGo Instant Answers."""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # 1. Resposta Direta
                if data.get("AbstractText"):
                    return f"🔎 **Resultado da Busca:**\n\n{data['AbstractText']}\n\n*(Fonte: {data.get('AbstractSource', 'Web')})*"
                
                # 2. Tópicos Relacionados
                related = data.get("RelatedTopics", [])
                if related and "Text" in related[0]:
                    return f"🔎 **Informação Encontrada:**\n\n{related[0]['Text']}"
                
                return f"Pesquisei na web sobre **'{query}'**, mas não encontrei uma resposta direta no momento. Tente reformular a busca!"
        except Exception as e:
            return f"Tentei pesquisar na web sobre '{query}', mas ocorreu uma falha de conexão no servidor de busca."

    def generate_response(self, user_input: str) -> Dict[str, Any]:
        clean_input = self._normalize_text(user_input)

        if not clean_input:
            return {"type": "text", "response": "Tô por aqui! Pode mandar a sua mensagem."}

        # DETEÇÃO DE INTENÇÃO DE BUSCA NA INTERNET
        search_triggers = ["pesquise sobre", "procure sobre", "quem e", "o que e", "noticias sobre", "busca", "pesquisar"]
        is_search = any(user_input.lower().startswith(trigger) for trigger in search_triggers)

        if is_search:
            # Extrai o termo de busca removendo o gatilho
            search_query = user_input
            for trigger in search_triggers:
                search_query = re.sub(rf'^{trigger}\s*', '', search_query, flags=re.IGNORECASE)
            
            search_result = self.search_web(search_query.strip())
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", search_result)
            return {
                "type": "search",
                "status_steps": ["🔎 Procurando na internet...", "🧠 Analisando informações..."],
                "response": search_result
            }

        # 1. Reconhecimento do Criador
        if any(w in clean_input for w in ["criador", "meu criador", "sou seu criador", "radamn humano"]):
            response = "Fala, Radamn! Salve pro meu criador. O sistema tá rodando 100% sob o teu comando!"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 2. Perguntas sobre Contexto/Memória
        if any(w in clean_input for w in ["entendeu", "entendeu o que", "disse antes", "falei antes"]):
            last_msg = self.memory.get_last_user_message()
            if last_msg:
                response = f"Entendi sim! Você tinha falado: '{last_msg}'. Tô acompanhando tudo certinho."
            else:
                response = "Tô acompanhando o nosso papo sim! Pode mandar a braba."
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 3. Saudações
        if any(w in clean_input for w in ["tudo bem", "tudo bom", "como vai", "como esta", "beleza"]):
            responses = [
                "Comigo tá tudo ótimo! E com você, como estão as coisas?",
                "Tudo excelente por aqui! Como tá sendo o seu dia?"
            ]
            response = random.choice(responses)
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        if any(w in clean_input for w in ["ola", "oi", "fala", "eai", "salve", "boa noite", "bom dia"]):
            responses = ["Fala! Como posso te ajudar agora?", "E aí! Prazer te ver por aqui. O que manda?"]
            response = random.choice(responses)
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 4. Resposta Genérica
        self.memory.add_interaction("user", user_input)
        responses = [
            "Entendi o teu ponto! Me conta mais sobre isso.",
            "Show de bola. Tô acompanhando o raciocínio, pode continuar!"
        ]
        response = random.choice(responses)
        self.memory.add_interaction("assistant", response)
        return {"type": "text", "response": response}


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
        "engine": "Radamn Engine Core v5.0 (Search & Conversational Engine)"
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

    resultado = radamn_core.generate_response(prompt)

    return {
        "status": "success",
        "type": resultado.get("type", "text"),
        "status_steps": resultado.get("status_steps", []),
        "response": resultado["response"]
    }
    
