import math
import random
import re
import urllib.parse
import urllib.request
import json
import unicodedata
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Radamn Engine Core", version="7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN ENGINE v7.0 - DIRECT KNOWLEDGE & FLEXIBLE SEARCH
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
        
        # Base de Conhecimento Local (Respostas Diretas)
        self.knowledge_base = {
            "inteligencia artificial": "Inteligência Artificial (IA) é o campo da ciência da computação dedicado a criar sistemas capazes de realizar tarefas que normalmente exigem inteligência humana, como raciocínio, aprendizado, reconhecimento de padrões e tomada de decisão.",
            "ia": "Inteligência Artificial é a capacidade de um sistema processar dados, aprender padrões e interagir com seres humanos de forma lógica.",
            "python": "Python é uma linguagem de programação de alto nível, amplamente utilizada em desenvolvimento web, automação, análise de dados e Inteligência Artificial.",
            "radamn": "Radamn AI é um ecossistema de inteligência artificial autônomo, desenvolvido com código próprio em Python sem dependência de APIs externas de LLM."
        }

    def _normalize_text(self, text: str) -> str:
        # Remove acentos e converte para minúsculas
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8').lower()
        text = re.sub(r'[^\w\s\+\-\*\/\=]', '', text)
        return text.strip()

    def evaluate_math_expression(self, user_input: str) -> Optional[str]:
        match = re.search(r'(\d+[\s\+\-\*\/\%]+\d+)', user_input)
        if match:
            expr = match.group(1).replace(" ", "")
            try:
                result = eval(expr)
                return f"Calculando passo a passo: {expr} = **{result}**."
            except Exception:
                return None
        return None

    def search_web(self, query: str) -> str:
        """Busca resiliente na Wikipedia API."""
        try:
            encoded_query = urllib.parse.quote(query)
            wiki_url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
            
            req = urllib.request.Request(
                wiki_url, 
                headers={'User-Agent': 'RadamnBot/1.0 (https://radamn.vercel.app)'}
            )
            
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get("extract"):
                        return f"🔎 **Resultado da Pesquisa ({query}):**\n\n{data['extract']}"
        except Exception:
            pass

        return f"Pesquisei sobre **'{query}'**, mas os servidores de busca não retornaram um resumo no momento."

    def generate_response(self, user_input: str) -> Dict[str, Any]:
        clean_input = self._normalize_text(user_input)

        if not clean_input:
            return {"type": "text", "response": "Tô por aqui! Pode mandar a sua mensagem."}

        # 1. VALIDAÇÃO MATEMÁTICA
        math_response = self.evaluate_math_expression(user_input)
        if math_response:
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", math_response)
            return {"type": "text", "response": math_response}

        # 2. BASE DE CONHECIMENTO LOCAL (Resposta Imediata)
        for key, info in self.knowledge_base.items():
            if key in clean_input:
                self.memory.add_interaction("user", user_input)
                self.memory.add_interaction("assistant", info)
                return {"type": "text", "response": info}

        # 3. PEDIDO DE CONTINUAÇÃO / SEQUÊNCIA
        if any(w in clean_input for w in ["da a sequencia", "me fala", "continue", "fala mais", "explique"]):
            last_msg = self.memory.get_last_user_message()
            if last_msg:
                search_query = re.sub(r'^(o que e|quem e|pesquise|sobre)\s*', '', self._normalize_text(last_msg)).strip()
                search_result = self.search_web(search_query)
                self.memory.add_interaction("user", user_input)
                self.memory.add_interaction("assistant", search_result)
                return {
                    "type": "search",
                    "status_steps": ["🔎 Pesquisando detalhes...", "🧠 Processando dados..."],
                    "response": search_result
                }

        # 4. INTENÇÃO DE BUSCA NA WEB
        search_triggers = ["pesquise sobre", "pesquisa sobre", "procure sobre", "o que e", "quem e", "busca"]
        is_search = any(clean_input.startswith(trigger) for trigger in search_triggers)

        if is_search:
            search_query = clean_input
            for trigger in search_triggers:
                search_query = re.sub(rf'^{trigger}\s*', '', search_query).strip()
            
            search_result = self.search_web(search_query)
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", search_result)
            return {
                "type": "search",
                "status_steps": ["🔎 Procurando na internet...", "🧠 Analisando dados..."],
                "response": search_result
            }

        # 5. EMPATIA E SUPORTE EMOCIONAL
        if any(w in clean_input for w in ["estressado", "cansado", "exausto", "dia dificil"]):
            response = "Sei como é... Dias assim pesam mesmo. Tenta dar uma respirada, mano. Quer trocar uma ideia pra desanuviar ou precisa de ajuda com algo?"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 6. RECONHECIMENTO DO CRIADOR
        if any(w in clean_input for w in ["criador", "meu criador", "sou seu criador", "radamn humano"]):
            response = "Fala, Radamn! Salve pro meu criador. O sistema tá rodando 100% sob o teu comando!"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 7. RESPOSTAS CONVERSACIONAIS GENÉRICAS
        self.memory.add_interaction("user", user_input)
        responses = [
            f"Entendi o seu ponto. Me fala mais sobre o que você precisa em relação a isso.",
            f"Tô acompanhando! Como prefere seguir?",
            f"Anotado por aqui. Qual é o próximo passo do nosso plano?"
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
        "engine": "Radamn Engine Core v7.0 (Direct Knowledge & Flexible Search)"
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
    
