ARG BASE_IMAGE=python:slim

##################################################
# LGPIO build
##################################################
FROM ${BASE_IMAGE} AS lgpio-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        swig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone https://github.com/joan2937/lg.git \
    && cd lg \
    && make \
    && make install


##################################################
# Project build
##################################################
FROM lgpio-build AS build

RUN pip install \
    poetry \
    wheel

WORKDIR /app
ENV VIRTUAL_ENV=/app
#RUN python -m venv --without-pip "${VIRTUAL_ENV}"
RUN python -m venv "${VIRTUAL_ENV}"

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --all-extras

COPY src src
RUN poetry install --only main --all-extras


##################################################
# Runtime
##################################################
FROM ${BASE_IMAGE} AS runtime

COPY --from=lgpio-build /usr/local/lib /usr/local/lib
RUN cd /usr/local/lib \
    && ldconfig

COPY --from=build /app /app

ENV GPIOZERO_PIN_FACTORY=lgpio

ENTRYPOINT ["/app/bin/fastapi", "run", "/app/src/gpio_api/app.py"]
CMD ["--port", "80"]
