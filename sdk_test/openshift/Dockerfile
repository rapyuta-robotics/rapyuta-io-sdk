FROM python:3.10-alpine

ENV PYTHONPATH /src
WORKDIR /src

COPY . /src
RUN apk add --no-cache --update coreutils curl
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x mc && mv mc /usr/local/bin/
RUN pip3 install pipenv coverage

CMD ["sdk_test/entrypoint.sh"]
