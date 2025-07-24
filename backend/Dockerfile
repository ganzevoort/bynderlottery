FROM python

RUN addgroup --gid 9999 code && \
    adduser --uid 9999 --gid 9999 --gecos '' --disabled-password code
RUN chmod 755 /home/code
ENV VIRTUALENV=/home/code/.venv
ENV PATH=$VIRTUALENV/bin:$PATH

USER code
WORKDIR /code
RUN python -m venv $VIRTUALENV
COPY ./requirements.txt ./
RUN pip install -U pip
RUN pip install -r requirements.txt
COPY ./ ./
RUN mkdir -p static logs
RUN python manage.py collectstatic --noinput
CMD ["/bin/bash", "start.sh"]
