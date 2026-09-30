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

app = FastAPI(title="Radamn Engine Core", version="6.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN ENGINE v6.5 - CONVERSACIONAL & SEARCH COMPLETO
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
        """Busca resiliente via Wikipedia API & DuckDuckGo."""
        try:
            # 1. Tenta Wikipedia API primeiro (alta estabilidade)
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
                        return f"🔎 **Resultado para '{query}':**\n\n{data['extract']}\n\n*(Fonte: Wikipedia)*"
        except Exception:
            pass

        # 2. Fallback para DuckDuckGo API
        try:
            ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            req = urllib.request.Request(
                ddg_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
                if data.get("AbstractText"):
                    return f"🔎 **Informação Encontrada:**\n\n{data['AbstractText']}"
        except Exception:
            pass

        return f"Busquei sobre **'{query}'**, mas os servidores de pesquisa não retornaram um resumo no momento. Tenta pesquisar com termos mais simples!"

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

        # 2. INTENÇÕES DE PESQUISA
        search_triggers = ["pesquise sobre", "pesquisa sobre", "procure sobre", "o que e", "quem e", "noticias sobre", "busca"]
        for trigger in search_triggers:
            if user_input.lower().startswith(trigger):
                search_query = re.sub(rf'^{trigger}\s*', '', user_input, flags=re.IGNORECASE).strip()
                search_result = self.search_web(search_query)
                self.memory.add_interaction("user", user_input)
                self.memory.add_interaction("assistant", search_result)
                return {
                    "type": "search",
                    "status_steps": ["🔎 Procurando na internet...", "🧠 Analisando dados..."],
                    "response": search_result
                }

        # 3. CORREÇÃO DE REPETIÇÃO / FEEDBACK DO USUÁRIO
        if any(w in clean_input for w in ["repetindo", "repetindo palavras", "mesma coisa", "travou"]):
            response = "Foi mal! Ajustei aqui o meu raciocínio pra não ficar repetindo a mesma resposta. O que você quer pesquisar ou conversar agora?"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 4. EMPATIA E SUPORTE
        if any(w in clean_input for w in ["cansado", "exausto", "dia dificil", "estressado"]):
            response = "Sei como é... Dias assim pesam mesmo. Tenta dar uma respirada, mano. Quer trocar uma ideia pra desanuviar ou precisa de ajuda com algo?"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 5. RECONHECIMENTO DO CRIADOR
        if any(w in clean_input for w in ["criador", "meu criador", "sou seu criador", "radamn humano"]):
            response = "Fala, Radamn! Salve pro meu criador. O sistema tá rodando 100% sob o teu comando!"
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 6. MEMÓRIA DE CONTEXTO
        if any(w in clean_input for w in ["entendeu", "disse antes", "falei antes", "aprofundar"]):
            last_msg = self.memory.get_last_user_message()
            if last_msg:
                response = f"Com certeza! A gente tava falando sobre: '{last_msg}'. O que mais você quer detalhar sobre isso?"
            else:
                response = "Tô acompanhando o nosso papo sim! Pode mandar a braba."
            self.memory.add_interaction("user", user_input)
            self.memory.add_interaction("assistant", response)
            return {"type": "text", "response": response}

        # 7. RESPOSTAS VARIADAS (SEM DUPILCAÇÃO)
        self.memory.add_interaction("user", user_input)
        responses = [
            f"Entendi perfeitamente o seu ponto sobre '{user_input}'. Como quer dar sequência?",
            f"Maneiro! Processando essa ideia. Me conta mais sobre isso.",
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
        "engine": "Radamn Engine Core v6.5 (Resilient Search & Adaptive Engine)"
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
    
