FROM node as builder

ENV PUBLIC_URL=https://sorterbot-static-wwccinrg.s3.eu-central-1.amazonaws.com
RUN mkdir /client
WORKDIR /client
COPY client /client
RUN yarn install
RUN yarn run build


FROM python:3.7

RUN mkdir /sbc_server
WORKDIR /sbc_server
COPY sbc_server/requirements.txt /sbc_server/requirements.txt
RUN pip3 install -r requirements.txt

ARG DEPLOY_REGION_ARG

EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV MODE="local"
ENV FROM_DOCKER=1
ENV DEPLOY_REGION=$DEPLOY_REGION_ARG

COPY sbc_server /sbc_server
COPY --from=builder /client/build/static /sbc_server/static
COPY --from=builder /client/build/index.html /sbc_server/templates/main.html
COPY --from=builder /client/build/favicon.ico /sbc_server/static/favicon.ico
ADD sbc_server/startup.sh /startup.sh
RUN chmod +x /startup.sh

RUN MODE=production python3 /sbc_server/manage.py collectstatic --noinput

CMD /startup.sh