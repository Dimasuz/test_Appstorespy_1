FROM dimasuz/ubuntu2004_python39:v4

COPY . /usr/src/app

ENTRYPOINT bash run.sh