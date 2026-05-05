FROM node:20-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY apps/web/package.json /app/apps/web/package.json
COPY packages/shared/package.json /app/packages/shared/package.json
COPY packages/shared/src /app/packages/shared/src

RUN npm install

COPY apps/web /app/apps/web

WORKDIR /app/apps/web
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]

