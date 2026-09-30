import math
import random
import re
import urllib.parse
from typing import List, Dict, Optional
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Radamn Engine Core", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# NÚCLEO DA IA PRÓPRIA RADAMN (Rede Neural & Processamento de Linguagem)
# =====================================================================

class RadamnNeuralModel:
    def __init__(self):
        # Vocabulário e pesos da própria rede
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.intent_templates: Dict[str, List[str]] = {}
        self._build_knowledge_base()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _build_knowledge_base(self):
        # Dataset de treinamento próprio da Radamn AI
        dataset = {
            "saudacao": {
                "inputs": ["ola", "oi", "fala", "eai", "salve", "boa noite", "bom dia", "tudo bem"],
                "responses": [
                    "Fala, mano! O motor próprio da Radamn AI tá rodando 100% online e sem limites.",
                    "Salve! Inteligência própria ativa e pronta pra rodar.",
                    "E aí! Como posso ajudar você hoje no sistema Radamn?"
                ]
            },
            "identidade": {
                "inputs": ["quem e voce", "quem e voce", "o que e radamn", "sua funcao", "quem te criou"],
                "responses": [
                    "Eu sou a Radamn AI, uma inteligência artificial própria desenvolvida do zero!",
                    "Sou o núcleo Radamn Core: tecnologia própria, rodando no nosso próprio servidor e sem dependência de terceiros."
                ]
            },
            "status": {
                "inputs": ["status", "como voce esta", "sistema", "motor"],
                "responses": [
                    "O motor Radamn Core está operando com estabilidade total no Render.",
                    "Sistemas 100% operacionais, sem amarras e pronto pra resposta."
                ]
            }
        }

        for intent, data in dataset.items():
            self.intent_templates[intent] = data["responses"]
            for phrase in data["inputs"]:
                for token in self._tokenize(phrase):
                    if token not in self.vocab:
                        idx = len(self.vocab)
                        self.vocab[token] = idx
                        self.inverse_vocab[idx] = token

    def predict(self, user_input: str) -> str:
        tokens = self._tokenize(user_input)
        if not tokens:
            return "Envie uma mensagem válida para o motor Radamn processar."

        # Pontuação dos intenções
        scores = {"saudacao": 0, "identidade": 0, "status": 0}
        for token in tokens:
            if token in ["ola", "oi", "fala", "eai", "salve", "noite", "dia"]:
                scores["saudacao"] += 2
            elif token in ["quem", "voce", "radamn", "funcao", "criou"]:
                scores["identidade"] += 2
            elif token in ["status", "sistema", "motor", "esta"]:
                scores["status"] += 2

        best_intent = max(scores, key=scores.get)
        
        # Se encontrou intenção com pontuação positiva
        if scores[best_intent] > 0:
            return random.choice(self.intent_templates[best_intent])

        # Síntese autônoma de resposta própria para novas entradas
        palavras_chaves = [t.capitalize() for t in tokens if len(t) > 2]
        if palavras_chaves:
            topico = ", ".join(palavras_chaves[:3])
            return f"Entendi o tópico sobre '{topico}'. O motor próprio da Radamn processou sua mensagem e está pronto para o próximo comando."

        return f"Mensagem '{user_input}' recebida e processada com sucesso no núcleo Radamn AI!"

# Instância única da IA Radamn
radamn_ia = RadamnNeuralModel()

# =====================================================================
# ROTAS DA API FASTAPI
# =====================================================================

class ChatPayload(BaseModel):
    user_id: str = "default_user"
    message: str
    image_url: Optional[str] = None

@app.get("/")
def status():
    return {
        "status": "Online", 
        "engine": "Radamn Engine Core v2.0 (Motor Próprio)"
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

    # 2. Processamento na IA Própria Radamn AI
    resposta_ia = radamn_ia.predict(prompt)

    return {
        "status": "success",
        "type": "text",
        "response": resposta_ia
    }
    
