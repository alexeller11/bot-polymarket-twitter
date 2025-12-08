import os
import random
from datetime import datetime
from fastapi import FastAPI
from tweepy import Client, TweepError

app = FastAPI()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

# Tweets prontos para postar - APENAS ESPORTES E CRIPTOMOEDAS - OPORTUNIDADES
TWEETS = [
    "🏆 Liverpool x Real Madrid em alta odds no Polymarket! Oportunidade de arbitragem detectada. Mercado está buscando equilíbrio. @Polymarket #Sports #Arbitrage",
    "💰 Bitcoin acumula ganhos expressivos! Mercado identifica consolidação de força em suportes. Profissionalizar posições agora é crítico. @Polymarket #Bitcoin #Crypto",
    "⚡ Ethereum em movimento! Nível de resistência 2.500 está sendo testado com volume crescente. Oportunidade em aberto para traders preparados. @Polymarket #Ethereum #DeFi",
    "🎯 Campeonato Brasileiro: padrão repetido em alguns times! Análise do Polymarket aponta mercado ineficiente. Traders atentos ganham com isso. @Polymarket #Sports #Trading",
    "🔥 Solana em recuperação! Rede mantém fluxos transacionais crescentes. Fundos institucionais voltam a posicionar. Oportunidade de longo prazo em formação. @Polymarket #SOL #Web3",
    "⚽ Copa Libertadores: mercado ainda repricia lances polêmicos! Decisões divergentes entre casas de apostas. Bom momento para quem analisa deep. @Polymarket #Sports #Libertadores",
    "🪙 XRP recupera volume após movimentação institucional. Padrões gráficos indicam acumulação. Mercado preparando próxima perna de alta. @Polymarket #XRP #Crypto",
    "📈 Basquete NBA: times de elite saem da comfort zone! Polymarket detecta repricing de mercado. Analistas que veem além do mainstream lucram. @Polymarket #NBA #Sports",
    "💎 DeFi tokens consolidam suportes após corretivo! TVL em crescimento. Oportunidade para quem entende o ciclo de mercado. @Polymarket #DeFi #Opportunity",
    "🚀 Cardano rompe resistências históricas! Atividade em rede bate recordes. Mercado de previsão premia quem viu isso vindo. @Polymarket #ADA #Crypto",
    "⛳ Masters Golf: mercado prega favoritos! Polymarket identifica gaps de repricing. Traders de props estão lucrando bem. @Polymarket #Golf #Sports #Props",
    "🔐 Bitcoin Lightning Network expande explosivamente! Transações diárias crescem 300%. Estrutura de rede muda o jogo. Mercado ainda não precificou tudo. @Polymarket #Bitcoin #Layer2"
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
