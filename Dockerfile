FROM quay.io/nushell/nu:devel
LABEL Maintainer vsochat@stanford.edu
# docker build -t vanessa/nushell-plugin-pokemon .
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install pokemon
WORKDIR /code
COPY nu_plugin_pokemon.py /usr/local/bin/nu_plugin_pokemon
