# Stage 1: build the SvelteKit static output
FROM oven/bun:1-alpine AS builder

WORKDIR /app

# Install dependencies (cached layer, deterministic via lockfile)
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Build the static site
COPY . ./
RUN bun run build

# Stage 2: serve the build with the non-root nginx variant on port 8080
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder --chown=nginx:nginx /app/build /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
