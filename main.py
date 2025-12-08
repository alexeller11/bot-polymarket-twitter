import os
import random
from datetime import datetime
from fastapi import FastAPI
from tweepy import Client, TweepError

app = FastAPI()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

# Tweets prontos para postar - SEM DEPENDENCIA DE API EXTERNA
TWEETS = [
    "🏆 Bitcoin en ALTA! Mercado aquecido hoje! Você tá dentro? @Polymarket #Polymarket #Sports",
    "⚡ Ethereum + 72% odds = ouro puro! Vale entrar agora? @Polymarket #DeFi",
    "📈 Copa do Mundo - Odds incríveis! Qualificação em fogo! @Polymarket #Polymarket",
    "🚀 Trump decisão 2024 + 85% chance. Mercado prevê X? @Polymarket #Crypto",
    "💎 Futebol - Liverpool vs Real Madrid. Odds imperdíveis! @Polymarket #Sports",
    "🪙 Bitcoin Lightning Network + 68% probabilidade. Não perca! @Polymarket #Web3 #Crypto",
    "⛓️ Ethereum ETF aprovação? 74% de chance! Vale comprar? @Polymarket #DeFi",
    "🔥 ALERT! Mercado de previsão em alta. Arbitragem detectada! @Polymarket #Arbitrage",
    "🌙 Neymar prox time? Odds curiosas no mercado! Vem debater! @Polymarket #Sports",
    "💰 Crypto rally incoming? Mercado aposta YES @Polymarket #Polymarket #Bitcoin",
]

@app.get("/")
def read_root():
    return {"message": "Hello world! From FastAPI running on Unicorn with Gunicorn. Using Python 3.11"}

@app.post("/postar-tweet")
def postar_tweet():
    try:
        # Pega tweet aleatório
        tweet = random.choice(TWEETS)
        
        # Posta no Twitter
        response = twitter_client.create_tweet(text=tweet)
        
        return {
            "status": "sucesso",
            "mensagem": "Tweet postado com sucesso!",
            "tweet": tweet,
            "timestamp": datetime.now().isoformat()
        }
    except TweepError as e:
        return {
            "status": "erro",
            "mensagem": f"Erro Twitter: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": str(e)
        }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
