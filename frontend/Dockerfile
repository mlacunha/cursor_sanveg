FROM node:20-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependência
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o resto do código
COPY . .

# Expõe a porta 3000
EXPOSE 3000

# Variáveis de ambiente para o Nuxt em Docker
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NODE_ENV=development

# Comando para rodar em desenvolvimento
CMD ["npm", "run", "dev"]
