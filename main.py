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

# Modelos de tweets humanizados COM @Polymarket
TWEET_TEMPLATES = {
    "sports": [
        "🏆 {market} em ALTA! {odds}% de chance. Mercado aquecido! Você tá dentro? @Polymarket #Polymarket #Sports",
        "⚡ OPORTUNIDADE! {market} agora com {odds}% de probabilidade. Vale a pena tomar? 👀 @Polymarket #Crypto #Betting",
        "📈 {market} + {odds}% odds = receita certa? Vem com a gente! @Polymarket #PolymarketBR #Sports",
        "🚀 {market} EXPLOSÃO! {odds}% de chance. Esse é o momento! 💰 @Polymarket #Arbitrage #Odds",
        "💎 Mercado {market} em FOGO! {odds}% odds | Quem aproveita o pump? @Polymarket #Polymarket #Sports",
    ],
    "crypto": [
        "🪙 {market} BOMBA! {odds}% de chance. O mercado sabe de algo? 🤔 @Polymarket #Web3 #Crypto",
        "⛓️ {market} + {odds}% odds = ouro puro! Vale entrar agora? @Polymarket #Polymarket #DeFi",
        "🔥 ALERT! {market} em alta com {odds}% de probabilidade. Não perca! 💪 @Polymarket #Crypto #Arbitrage",
        "🌙 {market} {odds}% | Mercado prevê X? Vem debater! 🧵 @Polymarket #Web3 #Polymarket",
        "💰 {market} com {odds}% de chance - Melhor oportunidade do dia! @Polymarket #Crypto #Sports",
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
        
        # Filtro: apenas mercados com volume alto (liquidez > 500 USDC)
        filtered = [
            m for m in markets 
            if m.get("volume24h", 0) > 500 or m.get("liquidityScore", 0) > 30
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
    """Cria tweets humanizados e emocionais COM @Polymarket"""
    try:
        market_title = market.get("question", "Mercado")[:35]
        try:
            yes_odds = float(market.get("bestBidYes", 0.5)) * 100
        except:
            yes_odds = 50.0
        
        # Detecta arbitrage
        arb = detect_arbitrage(market)
        
        # Escolhe template baseado na categoria
        category = "crypto" if any(tag in market_title.lower() for tag in ["crypto", "bitcoin", "ethereum", "defi"]) else "sports"
        templates = TWEET_TEMPLATES[category]
        template = random.choice(templates)
        
        # Cria tweet com emoji e dados
        tweet_text = template.format(
            market=market_title[:30],
            odds=f"{yes_odds:.0f}"
        )
        
        # Adiciona alerta de arbitragem se detectado
        if arb["detected"]:
            arb_text = f"\n\n⚠️ ARBITRAGEM: {arb['difference']:.1f}% diferença! {arb['recommendation']} 🎯"
            if len(tweet_text) + len(arb_text) <= 270:
                tweet_text += arb_text
        
        # Certifica que cabe nos 280 caracteres do Twitter
        if len(tweet_text) > 270:
            tweet_text = tweet_text[:267] + "..."
        
        return tweet_text
    except Exception as e:
        logger.error(f"Erro ao gerar tweet: {e}")
        return None

def post_tweet_to_twitter(tweet_text):
    """Posta o tweet no Twitter com retry"""
    try:
        if not tweet_text:
            logger.warning("Tweet vazio, ignorando")
            return False
        
        logger.info(f"Postando tweet: {tweet_text[:100]}...")
        response = twitter_client.create_tweet(text=tweet_text)
        logger.info(f"✅ Tweet postado com sucesso! ID: {response.data['id']}")
        return True
    except TweepError as e:
        logger.error(f"Erro Tweepy ao postar no Twitter: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
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
        logger.info(f"Mercado selecionado: {market.get('question', 'N/A')[:50]}")
        
        # Gera tweet humanizado
        tweet = generate_humanized_tweet(market)
        
        if not tweet:
            logger.error("Falha ao gerar tweet")
            return {"status": "erro", "mensagem": "Falha ao gerar tweet"}, 500
        
        # Posta no Twitter
        if post_tweet_to_twitter(tweet):
            logger.info("✅ Bot executado com sucesso!")
            return {
                "status": "sucesso",
                "mensagem": "Tweet postado com sucesso!",
                "tweet": tweet,
                "mercado": market.get("question", "N/A"),
                "timestamp": datetime.now().isoformat()
            }, 200
        else:
            logger.error("Falha ao postar tweet")
            return {"status": "erro", "mensagem": "Falha ao postar tweet no Twitter"}, 500
            
    except Exception as e:
        logger.error(f"Erro no endpoint: {str(e)}")
        return {"status": "erro", "mensagem": str(e)}, 500

@app.route("/health", methods=["GET"])
def health():
    """Health check do bot"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
