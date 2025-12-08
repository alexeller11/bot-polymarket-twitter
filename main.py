import os
import sys
import logging
import random
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import tweepy
from flask import Flask, jsonify

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Validar variáveis de ambiente ANTES de usar
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
if not TWITTER_BEARER_TOKEN:
    logger.error("❌ ERRO CRÍTICO: TWITTER_BEARER_TOKEN não definida!")
    logger.error("Configure a variável de ambiente no Cloud Run.")
    sys.exit(1)

try:
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    logger.info("✅ Tweepy client inicializado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar Tweepy: {e}")
    sys.exit(1)

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
        response = client.create_tweet(text=tweet_text)
        logger.info(f"✅ Tweet postado com sucesso: {tweet_text[:50]}...")
        logger.info(f"   Tweet ID: {response.data['id']}")
        return True
    except tweepy.Forbidden as e:
        logger.error(f"❌ ACESSO NEGADO ao X/Twitter: {e}")
        logger.error(f"   Verifique o TWITTER_BEARER_TOKEN e permissões da app.")
        return False
    except tweepy.TweepyException as e:
        logger.error(f"❌ Erro Tweepy: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao postar: {type(e).__name__}: {e}")
        return False

# Variável para monitorar scheduler
scheduler = None

def start_scheduler():
    """Inicia o scheduler em thread separada"""
    global scheduler
    try:
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(post_tweet, 'interval', hours=8, id='tweet_job')
        scheduler.start()
        logger.info("✅ Scheduler iniciado - tweets a cada 8 horas (3x por dia)")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar scheduler: {e}")
        raise

# Flask app para Cloud Run health checks
app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    """Health check endpoint para Cloud Run"""
    return jsonify({
        "status": "✅ Bot rodando!",
        "version": "2.0",
        "tweets_posted_per_day": "3x",
        "topics": ["Esportes", "Criptomoedas", "Polymarket"],
        "scheduler_active": scheduler is not None and scheduler.running,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/ping', methods=['GET'])
def ping():
    """Ping endpoint"""
    return jsonify({"pong": True, "timestamp": datetime.now().isoformat()}), 200

@app.route('/status', methods=['GET'])
def status():
    """Status detalhado do bot"""
    return jsonify({
        "bot_status": "running",
        "scheduler": {
            "active": scheduler is not None,
            "running": scheduler.running if scheduler else False,
            "jobs": len(scheduler.get_jobs()) if scheduler else 0
        },
        "twitter_token_configured": bool(TWITTER_BEARER_TOKEN),
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    logger.info("🚀 Iniciando Bot Polymarket Twitter...")
    
    # Iniciar scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Erro crítico ao iniciar scheduler: {e}")
        sys.exit(1)
    
    # Rodar Flask server na porta do Cloud Run
    port = int(os.getenv('PORT', 8080))
    logger.info(f"📡 Flask iniciando na porta {port}...")
    app.run(host='0.0.0.0', port=port, threaded=True, debug=False)
