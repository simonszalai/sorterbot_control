FROM node as builder

RUN mkdir /client
WORKDIR /client
COPY client /client
RUN yarn install
RUN yarn run build


FROM python:3.7

RUN mkdir /sbc_server
WORKDIR /sbc_server
COPY sbc_server /sbc_server
RUN pip3 install -r requirements.txt
COPY --from=builder /client/build/static /sbc_server/static/main
COPY --from=builder /client/build/index.html /sbc_server/templates/main.html
EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV AWS_DEFAULT_REGION "eu-central-1"

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]