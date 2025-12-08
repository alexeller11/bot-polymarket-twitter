# 🚀 GUIA COMPLETO DE DEPLOY - PowerShell (Windows)

## ⚠️ PRÉ-REQUISITOS

Certifique-se que você tem instalado:
- **Google Cloud SDK** (gcloud CLI)
- **Docker Desktop** (para testes locais)
- **Git** (para versionamento)
- **Python 3.9+** (para testes locais)

### Instalação do Google Cloud SDK (se não tiver):
```powershell
# Baixe em: https://cloud.google.com/sdk/docs/install-gcloud-sdk
# Ou execute:
choco install google-cloud-sdk -y
```

### Verificar instalações:
```powershell
gcloud --version
docker --version
git --version
python --version
```

---

## 📋 PASSO 1: Configurar Google Cloud Project

### 1.1 - Fazer login no Google Cloud
```powershell
gcloud auth login
```
(Será aberto seu navegador para autenticação)

### 1.2 - Definir seu Project ID
```powershell
# Substitua PROJETO_ID pelo seu ID (ex: project-c93016c1-6a2b-4fd0-bc4)
gcloud config set project PROJETO_ID
```

### 1.3 - Habilitar APIs necessárias
```powershell
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## 🔑 PASSO 2: Preparar Credenciais

### 2.1 - Criar arquivo de variáveis de ambiente
Crie um arquivo `.env.production` na raiz do repositório:

```
TWITTER_API_KEY=sua_api_key_aqui
TWITTER_API_SECRET=sua_api_secret_aqui
TWITTER_ACCESS_TOKEN=seu_access_token_aqui
TWITTER_ACCESS_TOKEN_SECRET=seu_access_token_secret_aqui
OPENAI_API_KEY=sua_openai_key_aqui
```

**⚠️ IMPORTANTE**: Nunca faça commit deste arquivo! Ele está em `.gitignore`.

### 2.2 - Armazenar secrets no Google Cloud Secret Manager
```powershell
# Para cada variável, execute:
$env:TWITTER_API_KEY | gcloud secrets create twitter-api-key --data-file=-
$env:TWITTER_API_SECRET | gcloud secrets create twitter-api-secret --data-file=-
$env:TWITTER_ACCESS_TOKEN | gcloud secrets create twitter-access-token --data-file=-
$env:TWITTER_ACCESS_TOKEN_SECRET | gcloud secrets create twitter-access-token-secret --data-file=-
$env:OPENAI_API_KEY | gcloud secrets create openai-api-key --data-file=-
```

---

## 🐳 PASSO 3: Build e Push da Imagem Docker

### 3.1 - Clone/Navegue até o repositório
```powershell
cd C:\seu_caminho\bot-polymarket-twitter
```

### 3.2 - Fazer login no Google Container Registry
```powershell
gcloud auth configure-docker
```

### 3.3 - Fazer build da imagem Docker
```powershell
# PROJETO_ID = seu project ID (ex: project-c93016c1-6a2b-4fd0-bc4)
docker build -t gcr.io/PROJETO_ID/bot-polymarket:latest .
```

### 3.4 - Push da imagem para Google Container Registry
```powershell
docker push gcr.io/PROJETO_ID/bot-polymarket:latest
```

---

## ☁️ PASSO 4: Deploy no Cloud Run

### 4.1 - Fazer deploy do serviço
```powershell
gcloud run deploy bot-polymarket `
  --image gcr.io/PROJETO_ID/bot-polymarket:latest `
  --platform managed `
  --region europe-west1 `
  --memory 512Mi `
  --cpu 1 `
  --timeout 3600 `
  --set-env-vars "POLYMARKET_API_URL=https://polymarket.com" `
  --allow-unauthenticated
```

### 4.2 - Visualizar status do deploy
```powershell
gcloud run services describe bot-polymarket --region europe-west1
```

---

## ⏰ PASSO 5: Configurar Scheduler para Posts Automáticos

### 5.1 - Criar Cloud Scheduler Job (para rodar diariamente às 9h)
```powershell
gcloud scheduler jobs create http bot-scheduler `
  --schedule="0 9 * * *" `
  --time-zone="Europe/Lisbon" `
  --uri="https://seu-url-do-cloud-run.run.app/schedule" `
  --http-method=GET `
  --oidc-service-account-email=PROJETO_NUMBER-compute@developer.gserviceaccount.com
```

### 5.2 - Teste o scheduler manualmente
```powershell
gcloud scheduler jobs run bot-scheduler
```

---

## 🧪 PASSO 6: Testar Localmente (ANTES de Deploy)

### 6.1 - Instalar dependências locais
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r agent-requirements.txt
```

### 6.2 - Rodar post-scheduler.py localmente
```powershell
# Terminal 1: Iniciar o agente IA interativo
python post-scheduler.py

# Siga as instruções para gerar posts humanizados
# O arquivo posts_agendados.json será criado
```

### 6.3 - Testar bot principal
```powershell
python main.py
```

---

## 📊 PASSO 7: Monitorar Logs

### 7.1 - Ver logs do Cloud Run em tempo real
```powershell
gcloud run services logs read bot-polymarket --region=europe-west1 --limit 50 --follow
```

### 7.2 - Ver logs do Cloud Build
```powershell
gcloud builds log --stream
```

### 7.3 - Ver histórico de execuções do Scheduler
```powershell
gcloud scheduler jobs describe bot-scheduler
```

---

## 🔍 TROUBLESHOOTING

### Erro: "Permission denied"
```powershell
gcloud auth login
gcloud config set project PROJETO_ID
```

### Erro: "Image not found"
```powershell
# Verificar se a imagem foi enviada corretamente
docker images | findstr "bot-polymarket"
gcloud container images list
```

### Cloud Run está fora do ar
```powershell
# Reimplementar serviço
gcloud run deploy bot-polymarket `
  --image gcr.io/PROJETO_ID/bot-polymarket:latest `
  --platform managed `
  --region europe-west1
```

### Posts não estão sendo publicados
1. Verificar credenciais do Twitter:
```powershell
gcloud secrets list
```
2. Verificar logs do Cloud Run (seção 7.1)
3. Testar `post-scheduler.py` localmente primeiro

---

## 📱 WORKFLOW DIÁRIO

### OPÇÃO 1: Automático (Recomendado)
1. Cloud Scheduler executa job às 9h
2. Agent IA gera sugestões automaticamente
3. Bot posta os tweets nos horários agendados
4. Monitorar logs para confirmar sucesso

### OPÇÃO 2: Manual (Controle Total)
```powershell
# 1. Executar scheduler localmente quando quiser
python post-scheduler.py

# 2. Revisar posts sugeridos em: posts_agendados.json
# 3. Editar/aprovar posts conforme necessário
# 4. Deixar Cloud Run rodar os posts nos horários agendados
```

---

## ✅ CHECKLIST FINAL

- [ ] Google Cloud SDK instalado e configurado
- [ ] Project ID definido corretamente
- [ ] APIs habilitadas (Cloud Build, Cloud Run, Cloud Scheduler)
- [ ] Secrets criadas no Secret Manager
- [ ] Docker build e push executados com sucesso
- [ ] Cloud Run deploy finalizado
- [ ] Scheduler job criado e testado
- [ ] Logs sendo monitorados
- [ ] Posts aparecendo normalmente
- [ ] Bot funcionando 24/7

---

## 🆘 SUPORTE

Se encontrar problemas:
1. Verificar logs: `gcloud run services logs read bot-polymarket --region=europe-west1 --limit 100`
2. Testar localmente primeiro
3. Validar credenciais das APIs
4. Verificar quotas do Google Cloud

**Boa sorte! 🚀**
