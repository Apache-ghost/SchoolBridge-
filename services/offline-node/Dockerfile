FROM node:18-alpine

WORKDIR /usr/src/app

# Install sqlite3 dependencies
RUN apk add --no-cache sqlite

COPY package.json ./
RUN npm install --production

COPY . .

# Create data directory for SQLite database
RUN mkdir -p data

EXPOSE 6000

CMD ["npm", "start"]