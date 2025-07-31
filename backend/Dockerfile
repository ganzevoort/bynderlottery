FROM python:3.13-alpine AS base

RUN addgroup --gid 9999 code && \
    adduser --uid 9999 --ingroup code --gecos '' --disabled-password code

WORKDIR /code
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Run linters and unittests
FROM base AS tester
COPY requirements.dev.txt ./
RUN pip install --no-cache-dir -r requirements.dev.txt
COPY ./ ./
RUN flake8
RUN black --check --diff .
ENV LAYER=test
RUN python manage.py collectstatic --noinput
RUN python manage.py test -v2
CMD ["/bin/true"]

# Production stage
FROM base AS production
COPY ./ ./
RUN mkdir -p static && python manage.py collectstatic --noinput
USER code
EXPOSE 8000
CMD ["/bin/sh", "start.sh"]

# Dev stage (default)
FROM base AS dev
COPY requirements.dev.txt ./
RUN pip install --no-cache-dir -r requirements.dev.txt
USER code
EXPOSE 8000
CMD ["/bin/sh", "start.sh"]
