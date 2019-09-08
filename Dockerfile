# Use an official image as a parent
FROM fedora:latest

# Set the working directory to /app
WORKDIR /app

# Prepare Fedora
RUN dnf -y update && dnf -y install httpd gcc sqlite python3 python3-devel && dnf clean all
# TODO Make id3edit optional to avoid clang-dependencies
# gcc and python3-devel are needed for some python modules


# TODO: IMPORTANT: Symlink /usr/bin/python -> /usr/bin/python3
# IMPORTANT: in Fedora, pip is calles pip3

# Copy MusicDB files into the image
COPY ./graphics ./graphics
COPY ./lib      ./lib
COPY ./mdbapi   ./mdbapi
COPY ./mod      ./mod
COPY ./webui    ./webui
COPY ./sql      ./sql
COPY ./musicdb  ./musicdb
COPY ./requirements.txt ./requirements.txt


# Install MusicDB python dependencies
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Setup Users and Groups
RUN groupadd -r musicdb && useradd  -d /data -s /usr/bin/bash -g musicdb -r -M musicdb

# Focus on a striped down installation of MusicDB without Icecaste, security-features, id3edit and AI support.
# Setup most important directories (MusicAI directories not needed)
RUN mkdir -p /data/{mdbstate,music}
RUN chown -R musicdb:musicdb /data
RUN chmod -R g+w /data
RUN chown -R musicdb:musicdb /app
COPY --chown=musicdb:musicdb ./share/default.jpg /data/artwork/.

# TODO /data/music must be outside the container - it will keep the music and be messed up with artwork and database-files
# TODO Problem: The container runs the server, no way to user other MusicDB modules like "add"

# Setup MusicDB
COPY ./docker/musicdb.ini /etc/musicdb.ini


#EXPOSE 80 9000
#   80: Apache
# 9000: MusicDB WebSocket Interface

# TODO: Run MusicDB Server
# TODO: Befor all servers get started, the databases must be created
CMD ["bash"]

