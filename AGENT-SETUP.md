# 🤖 Setup do Agente IA - Bot Polymarket

## Pré-requisitos

- ✅ Python 3.8+
- ✅ OpenAI API Key (obtenha em https://platform.openai.com/api-keys)
- ✅ Bot rodando no Cloud Run

---

## 1. Instalar Dependências

```bash
pip install -r agent-requirements.txt
```

---

## 2. Configurar Variáveis de Ambiente

Crie arquivo `.env` na raiz do projeto:

```bash
# .env
OPENAI_API_KEY=sk-proj-sua-chave-aqui
BOT_URL=https://seu-bot-url.run.app
```

**Obter OpenAI Key:**
1. Acesse https://platform.openai.com/account/api-keys
2. Clique em "Create new secret key"
3. Cole a chave no `.env`

**URL do Bot:**
- Copie de: Cloud Run Console → bot-polymarket → Service Details → URL

---

## 3. Rodar o Agente

```bash
python agent.py
```

---

## 4. Usar o Agente

Fale naturalmente em português:

```
👤 Você: Posta um tweet sobre Bitcoin atingindo 100k
🤖 Agente: ✅ Tweet postado com sucesso!

👤 Você: Qual é o status do bot agora?
🤖 Agente: {status JSON do bot}

👤 Você: Adiciona um novo tweet sobre Copa do Mundo
🤖 Agente: ✅ Tweet adicionado à lista!

👤 Você: Pausa o bot
🤖 Agente: ⏸️ Bot PAUSADO

👤 Você: Retoma o bot
🤖 Agente: ▶️ Bot RETOMADO
```

---

## 5. Integrar Endpoints no main.py

O bot precisa dos seguintes endpoints para o agente funcionar:

```python
# Em main.py, adicione:

@app.route('/post-manual', methods=['POST'])
def post_manual():
    data = request.json
    tweet_text = data.get('text')
    try:
        response = client.create_tweet(text=tweet_text)
        return {"status": "posted", "id": response.data['id']}
    except Exception as e:
        return {"error": str(e)}, 400

@app.route('/tweets', methods=['GET'])
def get_tweets():
    return {"tweets": TWEETS}

@app.route('/tweets/add', methods=['POST'])
def add_tweet():
    data = request.json
    TWEETS.append(data.get('text'))
    return {"status": "added", "total": len(TWEETS)}

@app.route('/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 10, type=int)
    # Retorna últimos logs (implementar conforme necessário)
    return {"logs": []}

@app.route('/scheduler/pause', methods=['POST'])
def pause_scheduler():
    scheduler.pause()
    return {"status": "paused"}

@app.route('/scheduler/resume', methods=['POST'])
def resume_scheduler():
    scheduler.resume()
    return {"status": "running"}
```

---

## 6. Troubleshooting

### "OPENAI_API_KEY não configurada"
```bash
# Verifique o arquivo .env
cat .env

# Ou configure diretamente:
export OPENAI_API_KEY="sk-proj-..."
```

### "Erro de conexão com o bot"
```bash
# Verifique se o bot está rodando:
curl https://seu-bot-url.run.app/ping

# Se retornar {"pong": true}, o bot está OK
```

### "LangChain módulo não encontrado"
```bash
pip install --upgrade langchain openai
```

---

## 7. Features do Agente

| Feature | Comando |
|---------|----------|
| **Postar Tweet** | "Posta um tweet sobre..." |
| **Ver Status** | "Qual é o status do bot?" |
| **Adicionar Tweet** | "Adiciona novo tweet sobre..." |
| **Ver Lista** | "Mostra os tweets" |
| **Ver Logs** | "Mostra os logs" |
| **Pausar Bot** | "Pausa o bot" |
| **Retomar Bot** | "Retoma o bot" |

---

## 8. Melhorias Futuras

- [ ] Integrar com Polymarket API para dados dinâmicos
- [ ] Adicionar persistência de histórico
- [ ] Suporte a múltiplos idiomas
- [ ] Dashboard web
- [ ] Integração com Discord

---

**Pronto! Seu agente IA está funcionando! 🚀**
