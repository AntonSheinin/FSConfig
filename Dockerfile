FROM python:3.10-slim

RUN groupadd --gid 1000 code && \
    useradd --create-home --gid 1000 --uid 1000 code
RUN mkdir -p /home/code/fsconfig
WORKDIR /home/code/fsconfig
COPY ./requirements.txt /home/code/fsconfig/
RUN pip3 install -r requirements.txt
COPY ./ /home/code/fsconfig/
RUN chown code:code /home/code/fsconfig
USER code
ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:8000 --reload --log-level debug -t 600 server:app

