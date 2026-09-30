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

app = FastAPI(title="Radamn Engine Core", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN ADVANCED BEHAVIORAL & REASONING ENGINE v6.0
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
        text = re.sub(r'[^\w\s\+\-\*\/\=\?]', '', text)
        return text.strip()

    def evaluate_math_expression(self, user_input: str) -> Optional[str]:
        """Comportamento 1: Validação Independente de Matemática/Cálculos."""
        # Extrai expressões matemáticas simples (ex: "quanto e 2 + 2", "5 * 10 e quanto?")
        match = re.search(r'(\d+[\s\+\-\*\/\%]+\d+)', user_input)
        if match:
            expr = match.group(1).replace(" ", "")
            try:
                result = eval(expr) # Avaliação matemática segura
                return f"Calculando passo a passo: {expr} = **{result}**."
            except Exception:
                return None
        return None

    def search_web(self, query: str) -> str:
        """Busca em tempo real na Web."""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get("AbstractText"):
                    return f"🔎 **Resultado da Pesquisa:**\n\n{data['AbstractText']}\n\n*(Fonte: {data.get('AbstractSource', 'Web')})*"
                
                related = data.get("RelatedTopics", [])
                if related and "Text" in related[0]:
                    return f"🔎 **Informação Encontrada:**\n\n{related[0]['Text']}"
                
                return f"Pesquisei sobre **'{query}'**, mas não encontrei um resumo direto na web."
        except Exception:
            return f"Não foi possível completar a pesquisa de '{query}' no momento por instabilidade na rede."

    def generate_response(self, user_input: str) -> Dict[str, Any]:
        clean_input = self._normalize_text(user_input)

        if not clean_input:
            return {"type": "text", "response": "Tô por aqui! Pode mandar a sua mensagem."}

        # COMPORTAMENTO 1: Validação de Matemática Independente
        math_response = self.evaluate_math_expression(user_input)
        if math_response:
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", math_response)
            return {"type": "text", "response": math_response}

        # DETEÇÃO DE BUSCA NA WEB
        search_triggers = ["pesquise sobre", "procure sobre", "quem e", "o que e", "noticias sobre", "busca", "pesquisar"]
        is_search = any(user_input.lower().startswith(trigger) for trigger in search_triggers)

        if is_search:
            search_query = user_input
            for trigger in search_triggers:
                search_query = re.sub(rf'^{trigger}\s*', '', search_query, flags=re.IGNORECASE)
            
            search_result = self.search_web(search_query.strip())
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", search_result)
            return {
                "type": "search",
                "status_steps": ["🔎 Procurando na internet...", "🧠 Analisando dados..."],
                "response": search_result
            }

        # COMPORTAMENTO 2: Empatia & Validação Emocional
        if any(w in clean_input for w in ["cansado", "exausto", "dia dificil", "estressado", "corrida"]):
            response = "Sei como é... Dias assim pesam mesmo. Tenta dar uma respirada, mano. Quer trocar uma ideia pra desparecer ou precisa de ajuda com algo?"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        if any(w in clean_input for w in ["feliz", "consegui", "deu certo", "vitoria", "top"]):
            response = "Boa! Notícia excelente! Tamo junto nessa conquista. O que vem a seguir no plano?"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # Reconhecimento do Criador
        if any(w in clean_input for w in ["criador", "meu criador", "sou seu criador", "radamn humano"]):
            response = "Fala, Radamn! Salve pro meu criador. O sistema tá rodando 100% sob o teu comando!"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # Contexto/Memória
        if any(w in clean_input for w in ["entendeu", "entendeu o que", "disse antes", "falei antes"]):
            last_msg = self.memory.get_last_user_message()
            if last_msg:
                response = f"Entendi sim! Você tinha falado: '{last_msg}'. Tô acompanhando tudo certinho."
            else:
                response = "Tô acompanhando o nosso papo sim! Pode mandar a braba."
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # COMPORTAMENTO 3: Respostas Diretas e Sem Fluff
        if any(w in clean_input for w in ["ola", "oi", "fala", "eai", "salve", "boa noite", "bom dia"]):
            responses = ["Fala! Em que posso somar hoje?", "Salve! Tudo certo por aí? O que manda?"]
            response = random.choice(responses)
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # Resposta Genérica
        self.memory.add_interaction("user", user_input)
        responses = [
            "Entendi a ideia. Quer aprofundar nisso ou puxar outro assunto?",
            "Visão! Tô acompanhando o raciocínio, manda a boa."
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
        "engine": "Radamn Engine Core v6.0 (Behavioral Engine)"
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
    
