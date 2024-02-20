ARG PYTHON=3.9.3
ARG FLAVOR=buster
FROM python:${PYTHON}-slim-${FLAVOR} AS base
ARG AIOHTTP

COPY dependencies.txt /workspace/
RUN apt-get update && \
    apt-get install -y build-essential tcpdump procps htop && \
    pip install -r /workspace/dependencies.txt && \
    pip install aiohttp==$AIOHTTP
RUN apt-get remove -y --purge build-essential && \
      apt-get autoremove -y && \
      rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace
COPY client.py /workspace/
COPY boot.bash /workspace/
RUN chmod +x /workspace/boot.bash


WORKDIR /workspace
ENTRYPOINT ["/workspace/boot.bash", "client.py"]
