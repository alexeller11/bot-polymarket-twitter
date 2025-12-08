FROM python:3.11-slim

WORKDIR /app

# Copiar arquivos
COPY requirements.txt .
COPY main.py .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Variáveis de ambiente
ENV PORT=8080 \
    PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 8080

# Executar app
CMD ["python", "-u", "main.py"]
