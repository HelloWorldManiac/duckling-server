FROM registry.sigma.sbrf.ru/dev/ci01978215/ci01978215_hr-platform_dev/javabase:v1.0

ENV DOCKER_BASE_IMAGE_VERSION=1.0.4

##install requirement tools
COPY /repos/pip.conf /etc/pip.conf
RUN yum install -y python36 python36-pip python36-wheel python36-devel gcc gcc-c++


##Setup env variables
ENV JAVA_HOME=/usr/lib/jvm/jre


WORKDIR /app
COPY python-duckling-master /app/python-duckling-master
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY wsgi.py /app/wsgi.py
COPY Extractors /app/Extractors

RUN pip3 install --no-cache  -r requirements.txt
RUN pip3 install ./python-duckling-master

USER 1001

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--bind", "0.0.0.0:8090", "-t", "90", "--workers", "1", "wsgi:app"]