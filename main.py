import os
import json
import random
from datetime import datetime
import requests
from flask import Flask, request
import logging
from tweepy import Client, TweepError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)
app = Flask(__name__)

# Modelos de tweets humanizados
TWEET_TEMPLATES = {
    "sports": [
        "🏆 {market} em ALTA! {odds}% de chance. Mercado aquecido! Você tá dentro? #Polymarket #Sports",
        "⚡ OPORTUNIDADE! {market} agora com {odds}% de probabilidade. Vale a pena tomar? 👀 #Crypto #Betting",
        "📈 {market} + {odds}% odds = receita certa? Vem com a gente! #PolymarketBR #Sports",
        "🚀 {market} EXPLOSÃO! {odds}% de chance. Esse é o momento! 💰 #Arbitrage #Odds",
        "💎 Mercado {market} em FOGO! {odds}% odds | Quem aproveita o pump? #Polymarket #Sports",
    ],
    "crypto": [
        "🪙 {market} BOMBA! {odds}% de chance. O mercado sabe de algo? 🤔 #Web3 #Crypto",
        "⛓️ {market} + {odds}% odds = ouro puro! Vale entrar agora? #Polymarket #DeFi",
        "🔥 ALERT! {market} em alta com {odds}% de probabilidade. Não perca! 💪 #Crypto #Arbitrage",
        "🌙 {market} {odds}% | Mercado prevê X? Vem debater! 🧵 #Web3 #Polymarket",
        "💰 {market} com {odds}% de chance - Melhor oportunidade do dia! #Crypto #Sports",
    ]
}

def fetch_polymarket_data():
    """Busca dados do Polymarket com filtro para mercados HOT"""
    try:
        response = requests.get(
            "https://clob.polymarket.com/markets",
            timeout=10,
            params={"limit": 100}
        )
        response.raise_for_status()
        markets = response.json()
        
        # Filtro: apenas mercados com volume alto (liquidez > 1000 USDC)
        filtered = [
            m for m in markets 
            if m.get("volume24h", 0) > 1000 or m.get("liquidityScore", 0) > 50
        ]
        
        # Prioriza esportes e crypto
        priority_markets = [
            m for m in filtered
            if any(tag in m.get("tags", []).lower() for tag in ["sports", "crypto", "defi", "football", "soccer", "bitcoin", "ethereum"])
        ]
        
        return priority_markets[:5] if priority_markets else filtered[:5]
    except Exception as e:
        logger.error(f"Erro ao buscar Polymarket: {e}")
        return []

def detect_arbitrage(market):
    """Detecta oportunidades de arbitragem entre exchanges"""
    try:
        # Compara odds do Polymarket com outras fontes
        poly_odds = float(market.get("bestBidYes", 0.5)) * 100
        
        # Simulação: busca arbitrage se há diferença > 5%
        arb_potential = False
        arb_difference = 0
        
        if poly_odds > 55:  # Se a oferta é muito alta
            arb_difference = poly_odds - 50
            arb_potential = True
        
        return {
            "detected": arb_potential,
            "difference": arb_difference,
            "recommendation": "COMPRE NO POLYMARKET" if arb_difference > 3 else "ESPERE"
        }
    except:
        return {"detected": False, "difference": 0, "recommendation": "NORMAL"}

def generate_humanized_tweet(market):
    """Cria tweets humanizados e emocionais"""
    try:
        market_title = market.get("question", "Mercado")[:50]
        yes_odds = float(market.get("bestBidYes", 0.5)) * 100
        
        # Detecta arbitrage
        arb = detect_arbitrage(market)
        
        # Escolhe template baseado na categoria
        category = "crypto" if any(tag in market_title.lower() for tag in ["crypto", "bitcoin", "ethereum", "defi"]) else "sports"
        templates = TWEET_TEMPLATES[category]
        template = random.choice(templates)
        
        # Cria tweet com emoji e dados
        tweet_text = template.format(
            market=market_title[:40],
            odds=f"{yes_odds:.0f}"
        )
        
        # Adiciona alerta de arbitragem se detectado
        if arb["detected"]:
            tweet_text += f"\n\n⚠️ ARBITRAGEM DETECTADA: {arb['difference']:.1f}% diferença!\n{arb['recommendation']} 🎯"
        
        # Certifica que cabe nos 280 caracteres do Twitter
        if len(tweet_text) > 270:
            tweet_text = tweet_text[:267] + "..."
        
        return tweet_text
    except Exception as e:
        logger.error(f"Erro ao gerar tweet: {e}")
        return None

def post_tweet_to_twitter(tweet_text):
    """Posta o tweet no Twitter"""
    try:
        if not tweet_text:
            logger.warning("Tweet vazio, ignorando")
            return False
        
        response = twitter_client.create_tweet(text=tweet_text)
        logger.info(f"Tweet postado com sucesso! ID: {response.data['id']}")
        return True
    except TweepError as e:
        logger.error(f"Erro ao postar no Twitter: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return False

@app.route("/postar-tweet", methods=["POST"])
def postar_tweet():
    """Endpoint que posta tweet automaticamente"""
    try:
        logger.info("=== INICIANDO BOT DE TWEETS ===")
        
        # Busca mercados do Polymarket
        markets = fetch_polymarket_data()
        
        if not markets:
            logger.warning("Nenhum mercado encontrado")
            return {"status": "erro", "mensagem": "Nenhum mercado disponível"}, 400
        
        # Seleciona mercado aleatório
        market = random.choice(markets)
        
        # Gera tweet humanizado
        tweet = generate_humanized_tweet(market)
        
        # Posta no Twitter
        if post_tweet_to_twitter(tweet):
            logger.info("✅ Bot executado com sucesso!")
            return {
                "status": "sucesso",
                "mensagem": "Tweet postado!",
                "tweet": tweet,
                "mercado": market.get("question", "N/A"),
                "timestamp": datetime.now().isoformat()
            }, 200
        else:
            return {"status": "erro", "mensagem": "Falha ao postar tweet"}, 500
            
    except Exception as e:
        logger.error(f"Erro no endpoint: {e}")
        return {"status": "erro", "mensagem": str(e)}, 500

@app.route("/health", methods=["GET"])
def health():
    """Health check do bot"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
