FROM python:3.13-slim AS shared

RUN apt update -qq && \
    apt install -qqy --no-install-recommends \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid 9999 code && \
    adduser --uid 9999 --gid 9999 --gecos '' --disabled-password code && \
    chmod 755 /home/code

WORKDIR /code
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt
COPY ./ ./
RUN mkdir -p static && \
    python manage.py collectstatic --noinput
USER code
EXPOSE 8000
CMD ["/bin/bash", "start.sh"]

# Production stage (same as shared for now)
FROM shared AS production

# Dev stage (default)
FROM shared AS dev
