import os
import json
import random
from datetime import datetime
import requests
from flask import Flask
import logging
from tweepy import Client, TweepError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)
app = Flask(__name__)

def buscar_mercados_polymarket(categoria="sports"):
    try:
        url = "https://clob.polymarket.com/markets"
        params = {"limit": 20}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        mercados = response.json()
        filtrados = []
        for mercado in mercados:
            tags = mercado.get("tags", [])
            if any(categoria.lower() in tag.lower() for tag in tags):
                filtrados.append(mercado)
        return filtrados[:5] if filtrados else mercados[:5]
    except Exception as e:
        logger.error(f"Erro: {e}")
        return []

def gerar_tweet_esportes():
    mercados = buscar_mercados_polymarket("sports")
    if not mercados:
        return "🏆 Confira mercados de esportes no @Polymarket!"
    mercado = random.choice(mercados)
    nome = mercado.get("question", "")[:70]
    volume = mercado.get("volumeNum", 0)
    tweet = f"🏆 MERCADO DE ESPORTES\n\n{nome}\n\nVolume: ${volume:,.0f}\n\nNegocie no @Polymarket 📊\n\n#Esportes"
    return tweet[:280]

def gerar_tweet_cripto():
    mercados = buscar_mercados_polymarket("crypto")
    if not mercados:
        return "💰 Mercados de cripto no @Polymarket!"
    mercado = random.choice(mercados)
    nome = mercado.get("question", "")[:70]
    liqui dez = mercado.get("liquidityNum", 0)
    tweet = f"📈 MERCADO DE CRIPTO\n\n{nome}\n\nLiquidez: ${liquidez:,.0f}\n\nNegocie no @Polymarket 🚀\n\n#Cripto"
    return tweet[:280]

def postar_tweet(conteudo):
    try:
        resposta = twitter_client.create_tweet(text=conteudo)
        logger.info(f"Tweet: {resposta['data']['id']}")
        return True, resposta['data']['id']
    except TweepError as e:
        logger.error(f"Erro: {e}")
        return False, str(e)

@app.route('/postar-tweet', methods=['GET', 'POST'])
def trigger_postar_tweet():
    try:
        hora = datetime.now().hour
        if hora % 2 == 0:
            conteudo = gerar_tweet_esportes()
            tipo = "Esportes"
        else:
            conteudo = gerar_tweet_cripto()
            tipo = "Cripto"
        sucesso, tweet_id = postar_tweet(conteudo)
        return {"status": "sucesso" if sucesso else "falha", "tipo": tipo, "tweet": conteudo, "tweet_id": tweet_id if sucesso else None}, 200 if sucesso else 500
    except Exception as e:
        logger.error(f"Erro: {e}")
        return {"erro": str(e)}, 500

@app.route('/saude', methods=['GET'])
def verificacao_saude():
    return {"status": "saudavel", "timestamp": datetime.now().isoformat(), "servico": "bot-polymarket"}, 200

@app.route('/', methods=['GET'])
def inicio():
    return {"msg": "Bot rodando", "endpoints": {"/postar-tweet": "POST", "/saude": "GET"}}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), debug=False)
