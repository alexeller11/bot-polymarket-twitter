import os
import random
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import tweepy

# Configurações
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# TWEETS SOBRE POLYMARKET - ESPORTES E CRIPTO
TWEETS = [
    "⚡ BTC TESTANDO 100K NA POLYMARKET AGORA\n🔥 15.2k traders posicionados\n💪 Vai quebrar? Comenta aí!",
    "💰 LOUCURA: Liverpool vs Real Madrid tem ODDS INSANAS na Polymarket\n⚽ Quem tá in? Valida!",
    "⚠️ ATENÇÃO: Volume EXPLODIU na Polymarket em 2h\n📈 Últimas horas pra entrar\n🎯 Oportunidade?",
    "🔴 CRYPTO CAINDO: Polymarket tá MOVIMENTADO\n📊 Shorts ganham na próxima 1h\n💎 Posição garantida?",
    "🏆 COPA AMÉRICA 2024: Odd 2.5 Argentina CAMPEÃ na Polymarket\n🇦🇷 Tá caro? Tá barato? DECIDE!",
    "🚀 ETHEREUM +5% EM 10MIN na Polymarket\n👀 Traders liquidados\n💥 Próximo pico = quando?",
    "⚡ URGÊNCIA: NBAFinalsGame7 em 30min na Polymarket\n🏀 Celtics ou Heat? Vocês acreditam?",
    "💰 DOGE PUMP DE 15% em Polymarket agora\n🐕 Seguindo Elon? Vai cair? FALA AÊEE!"
]

def post_tweet():
    """Publica um tweet aleatório a cada execução"""
    try:
        tweet_text = random.choice(TWEETS)
        client.create_tweet(text=tweet_text)
        print(f"✅ Tweet postado: {tweet_text[:50]}...")
    except Exception as e:
        print(f"❌ Erro ao postar: {e}")

# Scheduler para postar tweets 3x por dia
scheduler = BackgroundScheduler()
scheduler.add_job(post_tweet, 'interval', hours=8)  # A cada 8 horas = 3x por dia
scheduler.start()

# API Health Check
from flask import Flask
app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return {
        "status": "✅ Bot rodando!",
        "tweets_posted": "3x ao dia",
        "topics": ["Esportes", "Criptomoedas", "Polymarket"],
        "timestamp": datetime.now().isoformat()
    }

@app.route('/ping', methods=['GET'])
def ping():
    return {"pong": True}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
