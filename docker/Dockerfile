# Use an official image as a parent
FROM fedora:latest

# Set the working directory to /app
WORKDIR /app

# Prepare Fedora
RUN dnf -y update && dnf -y install httpd icecast sed dialog gcc clang sqlite python && dnf clean all
# TODO                                            ^^^^^^^^^^ ^^^^^^^^^
#                                                 ||||||||||  Make id3edit optional to avoid these dependencies
#                                                  Optimize docker image setup to not need those dependencies


# TODO: IMPORTANT: Symlink /usr/bin/python -> /usr/bin/python3
# IMPORTANT: in Fedora, pip is calles pip3


# Install MusicDB
#RUN git clone https://github.com/rstemmer/musicdb
#RUN cd musicdb
#RUN pip install --trusted-host pypi.python.org -r requirements.txt
#RUN cd scripts
# TODO: create a setup script specially for the docker image

#EXPOSE 443 666 9000
#  443: Apache
#  666: Icecast
# 9000: MusicDB WebSocket Interface

# TODO: Run MusicDB Server
CMD ["bash"]

