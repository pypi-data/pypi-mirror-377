# ProServe React Rendering Environment
# Advanced Docker setup for on-the-fly React component rendering

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl \
    bash

# Install global packages
RUN npm install -g \
    @babel/core \
    @babel/cli \
    @babel/preset-react \
    @babel/preset-env \
    webpack \
    webpack-cli \
    webpack-dev-server

# Create app structure
RUN mkdir -p /app/src /app/dist /app/components /app/cache

# Copy package configuration
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy React rendering server
COPY server.js ./
COPY webpack.config.js ./
COPY babel.config.js ./

# Copy default components
COPY components/ ./components/
COPY templates/ ./templates/

# Create cache directory with proper permissions
RUN chmod 777 /app/cache

# Expose ports
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Start command
CMD ["npm", "run", "start:server"]
