FROM node as builder

ARG RESOURCE_SUFFIX_ARG
ENV PUBLIC_URL=https://sorterbot-static-$RESOURCE_SUFFIX_ARG.s3.eu-central-1.amazonaws.com
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

EXPOSE 8000

ARG MODE_ARG
ARG DEPLOY_REGION_ARG

ENV MODE=$MODE_ARG
ENV DEPLOY_REGION=$DEPLOY_REGION_ARG
ENV PYTHONUNBUFFERED 1
ENV FROM_DOCKER=1

COPY sbc_server /sbc_server
COPY --from=builder /client/build/static /sbc_server/static
COPY --from=builder /client/build/index.html /sbc_server/templates/main.html
COPY --from=builder /client/build/favicon.ico /sbc_server/static/favicon.ico
ADD sbc_server/startup.sh /startup.sh
RUN chmod +x /startup.sh

RUN MODE=$MODE_ARG python3 /sbc_server/manage.py collectstatic --noinput

CMD /startup.sh

