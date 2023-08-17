FROM localstack/localstack:latest

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get -y -qq --no-install-recommends install \
  jq && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ENV PERSISTENT=1

COPY data /opt/localstack-data

COPY s3-init.sh /etc/localstack/init/ready.d/
