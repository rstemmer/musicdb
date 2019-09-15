# Use an official image as a parent
FROM fedora:latest

# Set the working directory
WORKDIR /opt/musicdb/server

# Prepare Fedora
RUN  dnf -y update && dnf -y install httpd sed rsync gcc sqlite icecast python3 python3-devel python3-gstreamer1 gstreamer1-plugins-good gstreamer1-plugins-bad-free vim && dnf clean all

# TODO Make id3edit optional to avoid clang-dependencies
# gcc and python3-devel are needed for some python modules


# TODO: IMPORTANT: Symlink /usr/bin/python -> /usr/bin/python3

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
#COPY ./docker/musicdb.ini /etc/musicdb.ini
ENV  TERM=xterm
RUN  useradd -m -s /usr/bin/bash user
RUN  mkdir -p /var/music

# Install MusicDB
RUN  chmod +x /src/docker/install.sh
RUN  /usr/bin/env bash -c /src/docker/install.sh

# Post-Install Tasks
RUN  usermod -a -G musicdb user
RUN  KEY="$(openssl rand -base64 32)" && sed -i -e "s;WSAPIKEY;\"$KEY\";g" /opt/musicdb/server/webui/config.js && sed -i -e "s;WSAPIKEY;\"$KEY\";g" /opt/musicdb/data/musicdb.ini
COPY ./docker/httpd.conf /etc/httpd/conf.d/musicdb.conf


# TODO /data/music must be outside the container - it will keep the music and be messed up with artwork and database-files
# TODO Problem: The container runs the server, no way to user other MusicDB modules like "add"

#EXPOSE 80 9000
#   80: Apache
# 9000: MusicDB WebSocket Interface

# Execute:
# httpd
# ./musicdb-boot.sh
# ./musicdb-start.sh

# TODO: Run MusicDB Server
# TODO: Befor all servers get started, the databases must be created
CMD ["bash"]

