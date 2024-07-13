FROM tiangolo/uwsgi-nginx-flask:python3.11

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY ./app /app
