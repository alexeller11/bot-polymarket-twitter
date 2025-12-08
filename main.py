import os
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from tweepy import Client, TweepError

app = FastAPI()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

# Global state do bot
bot_status = True  # Começa ativo

# Tweets com ALTO ENGAJAMENTO
TWEETS = [
    "🚨 VAI ROLAR HOJE: Liverpool vs Real Madrid é TRETA na Polymarket. Pessoal tá apostando pesado em um gol antes dos 30min. Vocês acreditam? @Polymarket #UCL",
    "💰 PAUSA! Bitcoin tá fazendo aquele movimento CLÁSSICO de consolidação... Quem tá olhando as odds na Polymarket sabe que a próxima perna VEM BOMBADA. @Polymarket #BTC",
    "⚡ ATENÇÃO: Ethereum testando 2.500 AGORA. Polymarket mostrando volume INSANO nos últimos 30min. Será que sai daqui? 👀 @Polymarket #ETH #DeFi",
    "🔥 BOMBAAAA: Brasileirão tá LOUCO hoje! Times que ninguém apostava tão ganhando. Polymarket tá repricitficando em TEMPO REAL. Quem tá ganhando aí? @Polymarket #Brasileirão",
    "🎯 GALERA: Solana VIROU a madrugada se recuperando. Fundos grandes voltaram a comprar. Polymarket detectou o movimento ANTES de acontecer. TALENTO ou SORTE? @Polymarket #SOL",
    "⚽ CALORÃO: Copa Libertadores tá POLÊMICA! Decisão do árbitro rendeu DÚZIAS de trades diferentes na Polymarket. Isso é OURO puro pra quem tá vendo. @Polymarket #Libertadores",
    "📈 URGENTE: XRP subiu 12% enquanto NINGUÉM tava olhando. Polymarket tá EXIBINDO que isso era previsível. Ficou pra trás? Acontece... @Polymarket #XRP #Crypto",
    "🏀 NBA TENSÃO: Lakers vs Celtics AGORA. Odds na Polymarket mudaram 5 VEZES só na pré-temporada. Mercado PENSA DEMAIS? @Polymarket #NBA #Sports",
    "💎 DEFI DETONANDO: TVL subiu ABSURDO. Polymarket identificou padrão ANTES dos normies. Isso é análise técnica ou MAGIA? @Polymarket #DeFi #Web3",
    "🚀 CARDANO EXPLOOOUU: Resistência de 2 ANOS rompida. Polymarket tá CHOVENDO dinheiro pra quem viu vindo. Saudade de estar lá? @Polymarket #ADA",
    "⛳ MASTERS GOLF HOJE: Favoritismo MORREU. Polymarket detectou anomalia nas odds. Traders de Props tão RINDO pra BANCO. @Polymarket #Golf #Sports",
    "🔐 BITCOIN LAYER2 EXPLODIU: Lightning Network processando MILHÕES. Estrutura de rede MUDOU PERM. Polymarket AINDA não precificou tudo isso. @Polymarket #Bitcoin",
    "🎪 CRYPTO MOMENT: Meme coin SUBIU mais que Bitcoin. Polymarket tá tipo 'isso faz sentido?' Caos organizado? SIM! @Polymarket #Crypto #Memes",
    "🏆 SPORTS MALUCURA: Time que MORREU na temporada tá REVIVENDO. Polymarket PULOU antes de todo mundo. Estratégia ou SORTE? @Polymarket #Sports",
    "⚙️ DeFi MOMENTO: Smart contracts RODANDO 24/7. TVL em crescimento EXPONENCIAL. Polymarket tá pronto pra próxima EXPLOSÃO? @Polymarket #DeFi"
]

def get_bot_status():
    """Pega status do bot (ativo/inativo)"""
    return bot_status

def set_bot_status(status):
    """Define status do bot"""
    global bot_status
    bot_status = status
    return True

@app.get("/")
def read_root():
    return {"message": "Bot Polymarket - Control Center"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Dashboard com botões Play/Stop"""
    status = get_bot_status()
    status_text = "🟢 ATIVO" if status else "🔴 INATIVO"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Polymarket - Control Center</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
            .container {{ background: white; border-radius: 15px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; }}
            h1 {{ color: #333; text-align: center; margin: 0 0 10px 0; }}
            .status {{ text-align: center; font-size: 24px; margin: 20px 0; font-weight: bold; }}
            .controls {{ display: flex; gap: 15px; margin: 30px 0; justify-content: center; }}
            button {{ padding: 15px 40px; font-size: 18px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; transition: all 0.3s; }}
            .play-btn {{ background: #10b981; color: white; }}
            .play-btn:hover {{ background: #059669; transform: scale(1.05); }}
            .stop-btn {{ background: #ef4444; color: white; }}
            .stop-btn:hover {{ background: #dc2626; transform: scale(1.05); }}
            .info {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .info h3 {{ margin: 0 0 10px 0; color: #1e40af; }}
            .info p {{ margin: 5px 0; color: #475569; }}
            .last-update {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
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
                <h3>💡 Como Funciona?</h3>
                <p><strong>PLAY:</strong> Ativa o bot para começar a postar tweets automaticamente</p>
                <p><strong>STOP:</strong> Pausa o bot, impedindo novos tweets</p>
                <p><strong>Status:</strong> {status_text}</p>
            </div>
            
            <div class="info">
                <h3>📊 Próximos Passos</h3>
                <p>Configure o Cloud Scheduler para automatizar postagens em horários específicos</p>
                <p>URL da API: <code>/postar-tweet</code></p>
            </div>
            
            <div class="last-update" id="lastupdate">Carregando...</div>
        </div>
        
        <script>
            function ativarBot() {{
                fetch('/ativar', {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(d => {{ alert('✅ ' + d.mensagem); location.reload(); }})
                    .catch(e => alert('❌ Erro: ' + e));
            }}
            
            function desativarBot() {{
                if(confirm('Tem certeza que deseja parar o bot?')) {{
                    fetch('/desativar', {{ method: 'POST' }})
                        .then(r => r.json())
                        .then(d => {{ alert('✅ ' + d.mensagem); location.reload(); }})
                        .catch(e => alert('❌ Erro: ' + e));
                }}
            }}
            
            function atualizarStatus() {{
                fetch('/status')
                    .then(r => r.json())
                    .then(d => {{
                        document.querySelector('.status').innerText = d.status ? '🟢 ATIVO' : '🔴 INATIVO';
                    }});
            }}
            
            setInterval(atualizarStatus, 5000);
        </script>
    </body>
    </html>
    """
    return html

@app.post("/ativar")
def ativar():
    """Ativa o bot"""
    set_bot_status(True)
    return {"status": "sucesso", "mensagem": "Bot ativado! 🟢"}

@app.post("/desativar")
def desativar():
    """Desativa o bot"""
    set_bot_status(False)
    return {"status": "sucesso", "mensagem": "Bot desativado! 🔴"}

@app.get("/status")
def status():
    """Retorna o status do bot"""
    ativo = get_bot_status()
    return {
        "ativo": ativo,
        "status": "🟢 ATIVO" if ativo else "🔴 INATIVO",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/postar-tweet")
def postar_tweet():
    """Posta um tweet se o bot está ativo"""
    # Verifica se bot está ativo
    if not get_bot_status():
        return {
            "status": "parado",
            "mensagem": "Bot está inativo. Ative o bot antes de postar!"
        }
    
    try:
        tweet = random.choice(TWEETS)
        response = twitter_client.create_tweet(text=tweet)
        
        return {
            "status": "sucesso",
            "mensagem": "Tweet postado com sucesso!",
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
