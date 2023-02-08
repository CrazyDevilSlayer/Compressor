FROM debian:11
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install \
    python3 python3-dev python3-dev python3-pip python3-venv 

RUN apt-get install wget python3-pip ffmpeg unzip p7zip-full curl busybox -y
ARG USER=root
USER $USER
RUN python3 -m venv venv
COPY . /app
WORKDIR /app
RUN chmod 777 /app
RUN pip3 install -r requirements.txt
RUN wget https://rclone.org/install.sh
RUN chmod 777 ./install.sh
RUN bash install.sh
RUN pip3 install -r requirements.txt
EXPOSE 5000
RUN chmod +x /app/start.sh
ENTRYPOINT ["./start.sh"]