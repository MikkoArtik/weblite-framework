ARG DOCKER_REGISTRY

FROM ${DOCKER_REGISTRY}/itm-python/python:3.12.6

WORKDIR /package

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

ENTRYPOINT ["sleep", "infinity"]
