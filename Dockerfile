FROM dimasuz/ubuntu2004_python310:v3

COPY . /usr/src/app

ENTRYPOINT bash run.sh