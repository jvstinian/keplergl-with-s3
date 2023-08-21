FROM python:3.9-slim-buster AS builder

RUN pip install --no-cache-dir --upgrade pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv requirements > /requirements.txt

FROM python:3.9-slim-buster

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get -y -qq --no-install-recommends install \
  gcc \
  python3-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /opt/keplergl-s3-svc

COPY --from=builder /requirements.txt .

ENV PYTHONPATH=/opt/keplergl-s3-svc-site-packages

RUN pip install --no-cache-dir --upgrade -t $PYTHONPATH setuptools && \
    pip install --no-cache-dir --upgrade -t $PYTHONPATH -r requirements.txt && \
    apt-get -y purge gcc python3-dev

