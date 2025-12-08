import os
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from tweepy import Client, TweepError

app = FastAPI()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

# Global state
bot_status = True

# TWEETS OTIMIZADOS PARA MÁXIMO ENGAJAMENTO
TWEETS = [
    # Padrão 1: URGÊNCIA + NÚMERO + POLYMARKET + CTA
    "🚨 BTC testando 100K NA POLYMARKET AGORA\n15.2k traders posicionados\n\nVai quebrar? Replica + Reply com sua previsão 👀\n#Polymarket #Crypto",
    "⚡ ETHEREUM: +8% em 30min na Polymarket\nMercado esperando break de 2.5K\n\nTa comprado ou vendido? RT + comenta 🚀\n#Polymarket #ETH",
    
    # Padrão 2: OPPORTUNITY
    "💰 LOUCURA: Liverpool vs Real Madrid tem ODDS INSANAS na Polymarket\n\nQuem tá in? Comenta aí! 🔥\n#UCL #Polymarket #Sports",
    "🎯 Brasileirão em CHAMAS\nPolymarket detectando padrões que ninguém vê\n\nTeu time tá rendendo? Replica isso 🏆\n#Brasileirão #Polymarket",
    
    # Padrão 3: FOMO
    "⏰ ATENÇÃO: Volume EXPLODIU na Polymarket\nÚltimas 2h melhor janela pra entrar\n\nVocê tá dormindo? Reply 😴\n#Polymarket #DeFi",
    "🔥 CARDANO (ADA) rompeu resistência\nPolymarket mostrando que algo BIG tá chegando\n\nQuem vai surfar essa onda? 🏄\n#Polymarket #ADA",
    
    # Padrão 4: SOCIAL PROOF
    "📊 3.2K traders na Polymarket apostando em Bitcoin hoje\nConsensus bullish?\n\nMonta posição ou observa? Comenta! 📈\n#Polymarket #BTC",
    "💎 SOLANA voltou à moda na Polymarket\n847 transações em 5min\n\nTá voltando ao topo? Tua opinião? 🚀\n#Polymarket #SOL",
    
    # Padrão 5: ANÁLISE RÁPIDA
    "🎪 XRP: Pump de 12% enquanto mundo dormia\nPolymarket detectou antes de todo mundo\n\nEsse é o sinal? Debate aqui! ⚔️\n#Polymarket #XRP",
    "⚽ COPA LIBERTADORES: Árbitro POLÊMICO rendeu DÚZIAS de trades na Polymarket\n\nMelhor mercado pra arbitragem? Fala aí! 🔥\n#Libertadores #Polymarket",
    
    # Padrão 6: BREAKING NEWS
    "🚨 BITCOIN LAYER2: Lightning Network EXPLODIU\nPolymarket ainda não precificou tudo isso\n\nTa vendo oportunidade? Comenta! 💥\n#Polymarket #Bitcoin",
    "📱 MEME COIN subiu MAIS que Bitcoin (sim, sério)\nPolymarket: 'Faz sentido? 🤔'\n\nCaos organizado? Responde aí 😂\n#Polymarket #Crypto",
    
    # Padrão 7: EXCLUSIVIDADE
    "🎯 EXCLUSIVO: Padrão raro detectado na Polymarket\n6 horas pra decidir\n\nTá dentro ou fica de fora? Avisa aqui! 🔮\n#Polymarket #Trading",
    "💎 DEFI EXPLOSION: TVL crescendo EXPONENCIAL\nPolymarket previsão: Próximo pump em 48h\n\nTa preparado? Comenta sua estratégia! 💰\n#Polymarket #DeFi",
]

def get_bot_status():
    return bot_status

def set_bot_status(status):
    global bot_status
    bot_status = status
    return True

@app.get("/")
def read_root():
    return {"message": "Bot Polymarket - Máximo Engajamento Ativado 🚀", "status": "ativo" if bot_status else "inativo"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    status = get_bot_status()
    status_text = "🟢 ATIVO" if status else "🔴 INATIVO"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Polymarket - Controle de Engajamento</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
            .container {{ background: white; border-radius: 15px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; }}
            h1 {{ color: #333; text-align: center; margin: 0 0 10px 0; }}
            .status {{ text-align: center; font-size: 28px; margin: 20px 0; font-weight: bold; }}
            .controls {{ display: flex; gap: 15px; margin: 30px 0; justify-content: center; }}
            button {{ padding: 15px 40px; font-size: 18px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; transition: all 0.3s; }}
            .play-btn {{ background: #10b981; color: white; }}
            .play-btn:hover {{ background: #059669; transform: scale(1.05); }}
            .stop-btn {{ background: #ef4444; color: white; }}
            .stop-btn:hover {{ background: #dc2626; transform: scale(1.05); }}
            .info {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .info h3 {{ margin: 0 0 10px 0; color: #1e40af; }}
            .info p {{ margin: 5px 0; color: #475569; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot Polymarket</h1>
            <div class="status">{status_text}</div>
            
            <div class="controls">
                <button class="play-btn" onclick="ativarBot()">▶ PLAY</button>
                <button class="stop-btn" onclick="desativarBot()">⏹ STOP</button>
            </div>
            
            <div class="info">
                <h3>📊 Status Atual</h3>
                <p>Status: {status_text}</p>
                <p>Tweets otimizados: 14 variações</p>
                <p>Padrão: URGÊNCIA + NÚMERO + POLYMARKET + CTA</p>
            </div>
            
            <div class="info">
                <h3>🎯 Estratégia de Engajamento</h3>
                <p>✅ Timing: Posts nos best hours</p>
                <p>✅ CTA: Pergunta/ação em cada tweet</p>
                <p>✅ Emojis: Padrão viral testado</p>
                <p>✅ Hashtags: #Polymarket sempre presente</p>
            </div>
        </div>
        
        <script>
            function ativarBot() {{
                fetch('/ativar', {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(d => {{ alert('✅ ' + d.mensagem); location.reload(); }})
                    .catch(e => alert('❌ Erro: ' + e));
            }}
            
            function desativarBot() {{
                if(confirm('Tem certeza?')) {{
                    fetch('/desativar', {{ method: 'POST' }})
                        .then(r => r.json())
                        .then(d => {{ alert('✅ ' + d.mensagem); location.reload(); }})
                        .catch(e => alert('❌ Erro: ' + e));
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html

@app.post("/ativar")
def ativar():
    set_bot_status(True)
    return {"status": "sucesso", "mensagem": "Bot ATIVADO! Tweets saindo 🚀"}

@app.post("/desativar")
def desativar():
    set_bot_status(False)
    return {"status": "sucesso", "mensagem": "Bot parado 🔴"}

@app.get("/status")
def status():
    ativo = get_bot_status()
    return {
        "ativo": ativo,
        "status": "🟢 ATIVO" if ativo else "🔴 INATIVO",
        "tweets_disponíveis": len(TWEETS),
        "padrão": "Engajamento máximo com CTA estratégico"
    }

@app.post("/postar-tweet")
def postar_tweet():
    if not get_bot_status():
        return {"status": "parado", "mensagem": "Bot inativo!"}
    
    try:
        tweet = random.choice(TWEETS)
        response = twitter_client.create_tweet(text=tweet)
        
        return {
            "status": "sucesso",
            "mensagem": "Tweet postado! 🚀",
            "tweet": tweet,
            "timestamp": datetime.now().isoformat()
        }
    except TweepError as e:
        return {"status": "erro", "mensagem": f"Erro Twitter: {str(e)}"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/health")
def health():
    return {"status": "ok", "bot_ativo": get_bot_status()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
