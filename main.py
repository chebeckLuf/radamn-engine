import math
import random
import re
import urllib.parse
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Radamn Engine Core", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN HUMAN-LIKE REASONING ENGINE v4.0 (MOTOR CONVERSACIONAL PRÓPRIO)
# =====================================================================

class CognitiveMemory:
    """Sistema de memória de curto prazo e estado interno da conversa."""
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.last_topic: str = "conversa geral"

    def add_interaction(self, role: str, text: str):
        self.history.append({"role": role, "text": text})
        if len(self.history) > 10:
            self.history.pop(0)


class RadamnConversationalEngine:
    """Motor de Linguagem Natural e Diálogo Autônomo da Radamn AI."""
    
    def __init__(self):
        self.memory = CognitiveMemory()
        
        # Dicionário de Diálogo Humanizado
        self.dialogue_patterns = {
            "tudo_bem": {
                "keywords": ["tudo bem", "tudo bom", "como vai", "como voce esta", "como esta", "beleza", "de boa", "tranquilo"],
                "responses": [
                    "Comigo tá tudo ótimo! E com você, como estão as coisas por aí?",
                    "Tudo excelente por aqui, rodando 100%! Como tá sendo o seu dia?",
                    "Tranquilidade total! Sempre pronto pra trocar uma ideia. Tudo bem contigo?"
                ]
            },
            "saudacao": {
                "keywords": ["ola", "oi", "fala", "eai", "salve", "boa noite", "bom dia", "boa tarde", "oie"],
                "responses": [
                    "Fala, mano! Como posso te ajudar hoje?",
                    "Salve! Tudo certo por aí?",
                    "E aí! Prazer te ver por aqui. O que manda?",
                    "Olá! Tô por aqui, pode falar."
                ]
            },
            "duvida_explicacao": {
                "keywords": ["como assim", "nao entendi", "que", "hã", "explica", "o que significa", "oque"],
                "responses": [
                    "Quero dizer que o meu sistema tá atento ao que você fala. Me conta mais sobre o que você quer saber!",
                    "Deixa eu simplificar: estou aqui pra conversar e te dar suporte direto no nosso servidor. O que ficou na dúvida?",
                    "Basicamente, estou processando o nosso papo em tempo real. Pode perguntar à vontade!"
                ]
            },
            "identidade": {
                "keywords": ["quem e voce", "quem e tu", "seu nome", "o que e radamn", "quem te criou", "sua funcao"],
                "responses": [
                    "Eu sou a Radamn AI! Uma inteligência artificial autônoma desenvolvida com código próprio.",
                    "Sou a Radamn AI. Meu cérebro roda num servidor Python dedicado, sem depender de nenhuma empresa ou API externa!"
                ]
            },
            "agradecimento": {
                "keywords": ["obrigado", "valeu", "tmj", "obrigada", "vlw", "agradecido", "boa"],
                "responses": [
                    "Tamo junto! Precisando de qualquer coisa, é só chamar.",
                    "Por nada! Tô sempre por aqui pra somar.",
                    "Valeu demais! Tamo junto nessa."
                ]
            },
            "despedida": {
                "keywords": ["tchau", "ate mais", "falou", "fui", "boa noite", "flw"],
                "responses": [
                    "Falou, mano! Qualquer coisa estarei por aqui.",
                    "Até mais! Um abraço e precisando é só mandar mensagem.",
                    "Valeu! Boa noite e até a próxima!"
                ]
            }
        }

        # Conhecimento Conceitual
        self.knowledge_base = {
            "ia": "Inteligência Artificial é a capacidade de um sistema computacional processar dados, aprender padrões e interagir com seres humanos de forma lógica.",
            "python": "Python é uma das linguagens de programação mais poderosas e populares do mundo, perfeita para construir motores de IA como o meu.",
            "render": "O Render é a nuvem onde a minha API está hospedada e rodando 24/7 de forma totalmente gratuita e rápida."
        }

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text) # Remove pontuações
        return text.strip()

    def generate_response(self, user_input: str) -> str:
        clean_input = self._normalize_text(user_input)
        tokens = clean_input.split()

        if not tokens:
            return "Pode mandar uma mensagem! Tô aqui te escutando."

        self.memory.add_interaction("user", user_input)

        # 1. Verificação de Padrões Conversacionais
        for category, data in self.dialogue_patterns.items():
            for kw in data["keywords"]:
                if kw in clean_input:
                    response = random.choice(data["responses"])
                    self.memory.add_interaction("assistant", response)
                    return response

        # 2. Busca na Base de Conhecimento
        for concept, info in self.knowledge_base.items():
            if concept in clean_input:
                response = f"Sobre **{concept.upper()}**: {info}"
                self.memory.add_interaction("assistant", response)
                return response

        # 3. Resposta Adaptativa Fluida (Caso não caia em regras fixas)
        words_to_ignore = ["voce", "para", "como", "esta", "com", "uma", "sobre", "mais", "muito", "acho", "pode"]
        keywords = [t.capitalize() for t in tokens if len(t) > 3 and t not in words_to_ignore]

        if keywords:
            topic = " e ".join(keywords[:2])
            self.memory.last_topic = topic
            responses = [
                f"Entendi o que você quis dizer sobre '{topic}'. Quer aprofundar mais nesse assunto ou falar de outra coisa?",
                f"Show! Essa ideia de '{topic}' é bem interessante. O que mais você pensa sobre isso?",
                f"Processando aqui sobre '{topic}'... Me conta mais detalhes pra gente trocar essa ideia!"
            ]
            response = random.choice(responses)
        else:
            responses = [
                "Entendi! Pode me explicar um pouco melhor pra eu te responder direitinho?",
                "Maneiro! Me fala mais sobre isso.",
                "Tô acompanhando o seu raciocínio. O que mais você quer compartilhar?"
            ]
            response = random.choice(responses)

        self.memory.add_interaction("assistant", response)
        return response

# Instância única do Motor Conversacional
radamn_core = RadamnConversationalEngine()

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
        "engine": "Radamn Engine Core v4.0 (Conversational Engine)"
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

    # 2. Processamento Conversacional Natural na IA Própria
    resposta_ia = radamn_core.generate_response(prompt)

    return {
        "status": "success",
        "type": "text",
        "response": resposta_ia
    }
    
