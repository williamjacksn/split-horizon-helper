FROM python:3.9.3-alpine3.13

COPY requirements.txt /split-horizon-helper/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /split-horizon-helper/requirements.txt

ENV APP_VERSION="2020.1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

COPY app.py /split-horizon-helper/app.py

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/split-horizon-helper/app.py"]
