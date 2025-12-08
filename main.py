import os
import random
from datetime import datetime
from fastapi import FastAPI
from tweepy import Client, TweepError

app = FastAPI()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

# Tweets com ALTO ENGAJAMENTO - Humanizados, com tendências do dia, focados em Polymarket
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
