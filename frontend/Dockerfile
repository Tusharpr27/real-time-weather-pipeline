# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build production bundle
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine AS runtime

WORKDIR /app

# Copy built files from builder
COPY --from=frontend-build /app/dist ./dist

# Install serve to run the production build
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://localhost:3000/ || exit 1

# Start production server
CMD ["serve", "-s", "dist", "-l", "3000"]
