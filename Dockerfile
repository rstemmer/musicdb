# Use an official image as a parent
FROM fedora:latest

# Set the working directory
WORKDIR /opt/musicdb/server

# Prepare Fedora
RUN  dnf -y update && dnf -y install httpd sed rsync gcc sqlite icecast python3 python3-devel python3-gstreamer1 gstreamer1-plugins-good gstreamer1-plugins-bad-free less && dnf clean all

# Copy MusicDB files into the image
RUN  mkdir /src
COPY ./graphics /src/graphics
COPY ./lib      /src/lib
COPY ./mdbapi   /src/mdbapi
COPY ./mod      /src/mod
COPY ./webui    /src/webui
COPY ./sql      /src/sql
COPY ./share    /src/share
COPY ./musicdb  /src/musicdb
COPY ./scripts  /src/scripts
COPY ./docker   /src/docker
COPY ./requirements.txt /src/requirements.txt
COPY ./VERSION  /src/VERSION


# Install MusicDB python dependencies
RUN  pip3 install --trusted-host pypi.python.org -r /src/requirements.txt

# Prepare MusicDB Installation
ENV  TERM=xterm
RUN  useradd -m -s /usr/bin/bash user
RUN  mkdir -p /var/music

# Install MusicDB
RUN  chmod +x /src/docker/install.sh
RUN  /usr/bin/env bash -c /src/docker/install.sh

# Post-Install Tasks
RUN  usermod -a -G musicdb user
RUN  KEY="$(openssl rand -base64 32)" && sed -i -e "s;WSAPIKEY;\"$KEY\";g" /opt/musicdb/server/webui/config.js && sed -i -e "s;WSAPIKEY;$KEY;g" /opt/musicdb/data/musicdb.ini
RUN  sed -i -e "s;address=127.0.0.1;address=0.0.0.0;g" /opt/musicdb/data/musicdb.ini
RUN  sed -i -e "s;--verbose;;g" /opt/musicdb/server/musicdb-start.sh
COPY ./docker/httpd.conf /etc/httpd/conf.d/musicdb.conf
COPY ./docker/container-boot.sh /opt/musicdb/server/container-boot.sh
RUN  chmod +x /opt/musicdb/server/container-boot.sh

CMD ["bash"]

