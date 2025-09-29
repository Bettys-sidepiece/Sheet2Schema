FROM node:20-alpine AS node_base
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# ---- Dev ----
FROM node_base AS dev
CMD ["npm", "run", "dev"]

# ---- Build ----
FROM node_base AS build
RUN npm run build

# ---- Production ----
FROM node_node:20-alpine AS prod
WORKDIR /app

COPY --from=build /app/package.json /app/package-lock.json* ./
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/node_modules ./node_modules

EXPOSE 3000
CMD ["npm", "start"]
