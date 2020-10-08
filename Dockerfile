

FROM fedora:32

RUN dnf update -y
RUN dnf install -y postgresql-devel gcc
RUN dnf install -y python-devel python-setuptools
RUN easy_install pip

RUN mkdir -p /covid19
COPY requirements.txt /covid19/requirements.txt
WORKDIR /covid19

RUN pip install -r requirements.txt
RUN pip install uwsgi

COPY . /covid19
RUN sed -i 's/covid19.models/models/g' server.py

CMD uwsgi --chdir=/covid19 \
    --module=wsgi:app \
    --master --pidfile=/tmp/covid19.pid \
    --http=0.0.0.0:5000 \
    --processes=4 \
    --uid=1000 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum