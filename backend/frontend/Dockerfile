FROM node:20-alpine

WORKDIR /app

# Копируем файлы манифеста зависимостей
COPY package*.json ./
RUN npm install

# Копируем код фронтенда
COPY . .

EXPOSE 5173

# Флаг --host 0.0.0.0 обязателен, чтобы Vite был доступен за пределами контейнера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]