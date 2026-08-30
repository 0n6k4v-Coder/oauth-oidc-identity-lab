FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY src/authorization-server/requirements.txt /code/authorization-requirements.txt
COPY src/resource-server/requirements.txt /code/resource-requirements.txt

RUN pip install --no-cache-dir \
    -r /code/authorization-requirements.txt \
    -r /code/resource-requirements.txt

COPY src/authorization-server/app /code/authorization-server/app
COPY src/resource-server/app /code/resource-server/app

COPY run-services.sh /code/run-services.sh

RUN chmod +x /code/run-services.sh

EXPOSE 8000 9000

CMD ["/code/run-services.sh"]