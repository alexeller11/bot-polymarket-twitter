#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AGENTE IA PARA CONTROLAR BOT POLYMARKET

Usa LangChain + OpenAI para permitir controle natural do bot via linguagem natural
Em português, sem limitações!
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Any, Optional

try:
    from langchain.llms import OpenAI
    from langchain.agents import initialize_agent, Tool, AgentType
    from langchain.memory import ConversationBufferMemory
except ImportError:
    print("❌ Erro: LangChain não instalado")
    print("Execute: pip install -r agent-requirements.txt")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURAÇÃO
# ============================================

BOT_URL = os.getenv("BOT_URL", "http://localhost:8080")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    print("❌ Erro: OPENAI_API_KEY não configurada!")
    print("Crie arquivo .env com: OPENAI_API_KEY=sua_chave")
    sys.exit(1)

# ============================================
# FERRAMENTAS DO AGENTE
# ============================================

def post_tweet_manual(tweet: str) -> str:
    """Posta um tweet AGORA (não espera 8 horas)"""
    try:
        resp = requests.post(f"{BOT_URL}/post-manual", json={"text": tweet}, timeout=10)
        if resp.status_code == 200:
            return f"✅ Tweet postado com sucesso!\nTexto: {tweet[:60]}..."
        return f"❌ Erro ao postar: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def get_bot_status() -> str:
    """Verifica status do bot em tempo real"""
    try:
        resp = requests.get(f"{BOT_URL}/status", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
        return f"❌ Erro: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def get_bot_logs() -> str:
    """Mostra os últimos logs do bot"""
    try:
        resp = requests.get(f"{BOT_URL}/logs?limit=10", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
        return f"❌ Erro: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def get_tweets_list() -> str:
    """Lista todos os tweets configurados"""
    try:
        resp = requests.get(f"{BOT_URL}/tweets", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            tweets = data.get('tweets', [])
            output = f"📋 Total de tweets: {len(tweets)}\n\n"
            for i, tweet in enumerate(tweets, 1):
                output += f"{i}. {tweet[:60]}...\n"
            return output
        return f"❌ Erro: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def add_new_tweet(tweet: str) -> str:
    """Adiciona um novo tweet à lista automática"""
    try:
        resp = requests.post(f"{BOT_URL}/tweets/add", json={"text": tweet}, timeout=10)
        if resp.status_code == 200:
            return f"✅ Tweet adicionado à lista!\nTexto: {tweet[:60]}..."
        return f"❌ Erro ao adicionar: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def pause_scheduler() -> str:
    """Pausa o scheduler de posts automáticos"""
    try:
        resp = requests.post(f"{BOT_URL}/scheduler/pause", timeout=10)
        if resp.status_code == 200:
            return "⏸️ Bot PAUSADO - não vai postar automaticamente"
        return f"❌ Erro: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def resume_scheduler() -> str:
    """Retoma o scheduler de posts automáticos"""
    try:
        resp = requests.post(f"{BOT_URL}/scheduler/resume", timeout=10)
        if resp.status_code == 200:
            return "▶️ Bot RETOMADO - volta a postar a cada 8 horas"
        return f"❌ Erro: {resp.text}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

# ============================================
# SETUP AGENTE
# ============================================

tools = [
    Tool(
        name="PostarTweet",
        func=post_tweet_manual,
        description="Posta um tweet AGORA no X/Twitter. Use quando o usuário quer postar algo específico imediatamente."
    ),
    Tool(
        name="StatusBot",
        func=get_bot_status,
        description="Verifica o status atual do bot: scheduler rodando, quantos tweets postados, etc."
    ),
    Tool(
        name="LogsBot",
        func=get_bot_logs,
        description="Mostra os últimos logs e erros do bot para debugar problemas."
    ),
    Tool(
        name="ListaTweets",
        func=get_tweets_list,
        description="Lista todos os tweets configurados que o bot posta automaticamente."
    ),
    Tool(
        name="AdicionarTweet",
        func=add_new_tweet,
        description="Adiciona um novo tweet à lista que será postado automaticamente. Use quando o usuário quer adicionar um novo tweet."
    ),
    Tool(
        name="PausarBot",
        func=pause_scheduler,
        description="Pausa o scheduler - o bot para de postar automaticamente."
    ),
    Tool(
        name="RetomarBot",
        func=resume_scheduler,
        description="Retoma o scheduler - o bot volta a postar a cada 8 horas."
    ),
]

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    human_prefix="👤 Você",
    ai_prefix="🤖 Agente"
)

llm = OpenAI(
    api_key=OPENAI_KEY,
    temperature=0.7,
    model="gpt-3.5-turbo"
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    max_iterations=5
)

# ============================================
# INTERFACE
# ============================================

def main():
    print("\n" + "="*60)
    print("🤖 AGENTE IA - BOT POLYMARKET v2.0")
    print("="*60)
    print("\n✅ Conectado ao bot em:", BOT_URL)
    print("\n📝 Fale naturalmente em português:")
    print("  • 'Posta um tweet sobre Bitcoin'")
    print("  • 'Qual é o status do bot?'")
    print("  • 'Adiciona um novo tweet sobre futebol'")
    print("  • 'Mostra os logs'")
    print("  • 'Pausa o bot'")
    print("  • 'Retoma o bot'")
    print("\nDigite 'sair' para encerrar")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("\n👤 Você: ").strip()
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\n👋 Até logo! Bot continua rodando...")
                break
            
            if not user_input:
                continue
            
            response = agent.run(user_input)
            print(f"\n🤖 Agente: {response}")
        except KeyboardInterrupt:
            print("\n\n👋 Até logo! Bot continua rodando...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()
