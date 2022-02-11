FROM node:latest
RUN mkdir /app
ADD ./js /app
WORKDIR /app
RUN npm install
