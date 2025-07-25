# build environment
FROM node:16-alpine as build
WORKDIR /app/frontend
COPY frontend/package.json .
COPY frontend/package-lock.json .
RUN npm ci
COPY frontend .
RUN ls -la /app/frontend
COPY frontend/src /app/frontend/src
RUN ls -la /app/frontend/src
RUN npm run build

# production environment
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
