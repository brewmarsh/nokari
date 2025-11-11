# build environment
FROM node:20-alpine AS build
WORKDIR /app
COPY . .
RUN npm ci
RUN npm test
RUN npm run build

# production environment
FROM nginx:stable-alpine
RUN apk upgrade --no-cache
RUN apk add --no-cache netcat-openbsd
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["/app/wait-for-it.sh", "backend:8000", "--", "nginx", "-g", "daemon off;"]
