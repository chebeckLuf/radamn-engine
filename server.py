from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os

app = FastAPI(title="Radamn Dedicated AVS Core - Ultra Performance", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "LuffyNox/radamn-ai-v1"
HF_TOKEN = os.getenv("HF_TOKEN")

print("⚡ Inicializando Radamn Engine...")

generator = None
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        token=HF_TOKEN,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        low_cpu_mem_usage=True
    )
    
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    print("✅ Modelo Radamn AI pronto para inferência de alta velocidade!")
except Exception as e:
    print(f"⚠️ Erro ao carregar o modelo: {e}")

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9

@app.get("/")
def health_check():
    return {
        "status": "Online",
        "engine": "Radamn Native Core v2",
        "gpu_available": torch.cuda.is_available(),
        "model_loaded": generator is not None
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    if not generator:
        raise HTTPException(status_code=503, detail="O modelo está a ser carregado ou indisponível.")

    try:
        # Monta o prompt formatado a partir do histórico de mensagens
        full_prompt = ""
        for msg in req.messages:
            full_prompt += f"{msg.role.capitalize()}: {msg.content}\n"
        full_prompt += "Assistant:"

        outputs = generator(
            full_prompt,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            do_sample=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )

        generated_text = outputs[0]["generated_text"]
        
        # Extrai apenas a nova resposta gerada
        if full_prompt in generated_text:
            response_content = generated_text.split("Assistant:")[-1].strip()
        else:
            response_content = generated_text.strip()

        return {
            "id": "radamn-chat",
            "object": "chat.completion",
            "model": MODEL_NAME,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da IA: {str(e)}")
      
