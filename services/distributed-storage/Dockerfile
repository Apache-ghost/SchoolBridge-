FROM node:18-alpine

WORKDIR /usr/src/app

# Install dependencies
COPY package*.json ./
RUN npm install --production

# Create data directory
RUN mkdir -p ./data

# Copy source code
COPY . .

# Expose port
EXPOSE 7000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:7000/health || exit 1

# Start the service
CMD ["node", "server.js"]