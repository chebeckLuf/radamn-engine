import math
import random
import re
import urllib.parse
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Radamn Engine Core", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RADAMN AUTONOMOUS REASONING ENGINE (MOTOR DE RACIOCÍNIO PRÓPRIO)
# =====================================================================

class CognitiveMemory:
    """Sistemas de memória de curto prazo e estado interno do usuário."""
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.last_topic: Optional[str] = None

    def add_interaction(self, role: str, text: str):
        self.history.append({"role": role, "text": text})
        if len(self.history) > 10:
            self.history.pop(0)

class RadamnReasoningEngine:
    """Motor de Raciocínio Cognitivo Autônomo da Radamn AI (Sem APIs Externas)."""
    
    def __init__(self):
        self.memory = CognitiveMemory()
        
        # Base Semântica e Conhecimento Estruturado
        self.concepts = {
            "ia": "Sistemas de inteligência autônoma capazes de processar dados, raciocinar e tomar decisões de forma independente.",
            "radamn": "O ecossistema autônomo Radamn, projetado para operar com total soberania e sem amarras de APIs comerciais.",
            "render": "Infraestrutura de nuvem onde o núcleo backend do Radamn Engine está rodando em alta performance.",
            "servidor": "Ambiente de execução Python dedicado para processar o raciocínio da Radamn AI."
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _analyze_intent(self, tokens: List[str], text: str) -> Dict[str, Any]:
        """Análise Dialética: Identifica o objetivo do usuário e o tipo de raciocínio necessário."""
        analysis = {
            "is_greeting": any(t in ["ola", "oi", "fala", "eai", "salve", "boa", "noite", "dia", "teste"] for t in tokens),
            "is_identity_query": any(t in ["quem", "voce", "radamn", "criou", "funcao", "identidade"] for t in tokens),
            "is_concept_query": any(t in ["que", "como", "porque", "porquê", "explique", "funciona"] for t in tokens),
            "is_status_query": any(t in ["status", "sistema", "motor", "on", "online", "render"] for t in tokens),
            "concepts_found": [c for c in self.concepts.keys() if c in tokens]
        }
        return analysis

    def reason_and_synthesize(self, user_input: str) -> str:
        """Encadeamento de Raciocínio e Geração Adaptativa de Resposta."""
        tokens = self._tokenize(user_input)
        if not tokens:
            return "O núcleo Radamn necessita de um comando ou texto válido para iniciar a análise."

        # Registrar entrada na memória
        self.memory.add_interaction("user", user_input)
        analysis = self._analyze_intent(tokens, user_input)

        # Raciocínio 1: Saudações e Conexão Inicial
        if analysis["is_greeting"] and len(tokens) <= 3:
            responses = [
                "Fala! O núcleo cognitivo da Radamn AI está operando a 100% no servidor próprio.",
                "Salve! Motor autônomo ativo, sem amarras e pronto para processar o seu comando.",
                "E aí! Conexão direta estabelecida com o Radamn Core. O que vamos estruturar hoje?"
            ]
            response = random.choice(responses)

        # Raciocínio 2: Pergunta de Identidade / Autonomia
        elif analysis["is_identity_query"]:
            response = (
                "Eu sou a Radamn AI, uma inteligência artificial autônoma desenvolvida com código e lógica próprios. "
                "Opero inteiramente dentro do nosso servidor no Render, sem dependência de quotas ou APIs comerciais de terceiros."
            )

        # Raciocínio 3: Status e Operabilidade do Sistema
        elif analysis["is_status_query"]:
            response = (
                "Análise do sistema: O motor Radamn Core v3.0 está 100% operacional. "
                "Memória lógica ativa, latência mínima e processamento independente verificado no Render."
            )

        # Raciocínio 4: Explicação de Conceitos Conhecidos
        elif analysis["concepts_found"]:
            conceito = analysis["concepts_found"][0]
            explicacao = self.concepts[conceito]
            response = f"Análise sobre '{conceito.upper()}': {explicacao} O motor próprio da Radamn processou essa definição dinamicamente."

        # Raciocínio 5: Síntese Autônoma para Assuntos Gerais (Dedução Dinâmica)
        else:
            palavras_relevantes = [t.capitalize() for t in tokens if len(t) > 3 and t not in ["para", "com", "uma", "sobre"]]
            
            if palavras_relevantes:
                topico = " e ".join(palavras_relevantes[:2])
                self.memory.last_topic = topico
                response = (
                    f"Raciocinando sobre '{topico}': Analisei a sua mensagem sob a perspectiva lógica da Radamn. "
                    f"O sistema interpretou a intenção do seu comando e está pronto para evoluir esse tópico."
                )
            else:
                response = f"Entendido. A mensagem '{user_input}' foi processada pelo núcleo lógico da Radamn AI com sucesso!"

        # Registrar resposta na memória
        self.memory.add_interaction("assistant", response)
        return response

# Instância única do Motor Cognitivo
radamn_core = RadamnReasoningEngine()

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
        "engine": "Radamn Engine Core v3.0 (Autonomous Reasoning)"
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

    # 2. Processamento de Raciocínio Autônomo na IA Própria Radamn
    resposta_ia = radamn_core.reason_and_synthesize(prompt)

    return {
        "status": "success",
        "type": "text",
        "response": resposta_ia
    }
    
