FROM node

RUN mkdir /client
WORKDIR /client
COPY . /client
RUN yarn install
EXPOSE 3000

CMD ["yarn", "start"]