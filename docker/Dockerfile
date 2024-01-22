FROM dimasuz/ubuntu2004_python39:v1

# попробовать
# sudo apt install lsb-release curl gpg
# sudo apt-get update
# sudo apt-get install redis

COPY requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app
RUN python3 -m pip install --no-cache-dir -r requirements.txt