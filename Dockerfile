FROM python:3.12-slim as builder

ARG TESTING=0
WORKDIR /app

# ENV TZ Europe/Moscow
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH=.
ENV PYTHONUNBUFFERED 1
#ENV ENVIRONMENT prod
ENV TESTING ${TESTING}

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN rm -rf /root/.cache/pip \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
