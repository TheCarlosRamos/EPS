<<<<<<< HEAD
FROM node:22-alpine AS build
=======
FROM node:18-alpine
>>>>>>> 9ae8a72cc681d65889500874d7843ccc25c0a5fe

WORKDIR /app

COPY package*.json ./
<<<<<<< HEAD
RUN npm install

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

RUN apk add --no-cache gettext openssl

COPY docker/nginx.conf.template /etc/nginx/templates/nginx.conf.template
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]
=======

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
>>>>>>> 9ae8a72cc681d65889500874d7843ccc25c0a5fe
