# Use uma imagem oficial do Python como base
FROM python:3.11-slim

# Define as variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o contêiner
COPY . .

# Coleta os arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta que a aplicação vai usar
EXPOSE 8000
