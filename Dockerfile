# Multi-stage build para imagem minimal
FROM python:3.11-slim as builder

# Instalar dependencias de build (temporário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
COPY requirements.txt .

# Compilar wheels
RUN pip install --no-cache-dir --user --no-warn-script-location \
    -r requirements.txt

# Runtime image
FROM python:3.11-slim

# Adicionar labels para Cloud Run
LABEL org.opencontainers.image.description="Bot automatizado que posta tweets sobre Polymarket"
LABEL org.opencontainers.image.version="2.0"

WORKDIR /app

# Copiar apenas os deps compilados (não precisa de gcc na runtime)
COPY --from=builder /root/.local /root/.local

# Copiar codigo da app
COPY requirements.txt .
COPY main.py .

# Configurar PATH para usar pip packages do usuario
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Health check (Cloud Run usa isso para validar)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/ping').read(); print('OK')"

# Expor porta
EXPOSE 8080

# Garantir que app inicia corretamente
CMD ["python", "-u", "main.py"]
