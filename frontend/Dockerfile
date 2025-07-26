# build environment
FROM node:20-alpine as build
WORKDIR /app
COPY package.json .
COPY package-lock.json .
COPY public ./public
COPY src ./src
RUN ls -la /app/src
RUN npm ci
RUN npm run build

# production environment
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
