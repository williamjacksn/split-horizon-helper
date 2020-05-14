FROM python:3.8.2-alpine3.11

COPY requirements.txt /split-horizon-helper/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /split-horizon-helper/requirements.txt
