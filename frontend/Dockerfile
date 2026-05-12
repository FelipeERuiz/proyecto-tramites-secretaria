FROM node:14-alpine

WORKDIR /app

# Instalar dependencias primero (mejor caché de Docker)
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]