FROM python:3.13-alpine AS base

RUN addgroup --gid 9999 code && \
    adduser --uid 9999 --ingroup code --gecos '' --disabled-password code

WORKDIR /code

# Install dependencies first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Development dependencies stage
FROM base AS dev-deps
COPY requirements.dev.txt ./
RUN pip install --no-cache-dir -r requirements.dev.txt

# Testing stage: run linters and unittests
FROM dev-deps AS tester
COPY ./ ./
RUN flake8
RUN black --check --diff .
ENV LAYER=test
RUN python manage.py collectstatic --noinput
RUN python manage.py test -v2

# Production stage
FROM base AS production
COPY ./ ./
RUN mkdir -p static && python manage.py collectstatic --noinput
USER code
EXPOSE 8000
CMD ["/bin/sh", "start.sh"]

# Development stage (default)
FROM dev-deps AS dev
USER code
EXPOSE 8000
CMD ["/bin/sh", "start.sh"]
