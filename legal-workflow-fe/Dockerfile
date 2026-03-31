# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Write VITE_API_URL into .env so vite picks it up at build time
ARG VITE_API_URL=https://lww-backend-21672960606.asia-southeast1.run.app
RUN echo "VITE_API_URL=${VITE_API_URL}" > .env

RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
