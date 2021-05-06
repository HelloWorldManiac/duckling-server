FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/ && \
    rm -rf /var/cache/oracle-jdk8-installer;

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

RUN apt-get update && apt-get install -y \
        software-properties-common
    RUN add-apt-repository ppa:deadsnakes/ppa
    RUN apt-get update && apt-get install -y \
        python3.7 \
        python3-pip
    RUN python3.7 -m pip install pip
    RUN apt-get update && apt-get install -y \
        python3-distutils \
        python3-setuptools

WORKDIR /usr/src/app
COPY . /usr/src/app/

RUN pip3 install -r requirements.txt
RUN pip3 install ./python-duckling-master


CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--bind", "0.0.0.0:8090", "-t", "90", "--workers", "1", "wsgi:app"]
