FROM ubuntu:14.04
MAINTAINER Andrew Ferrier <andrew.ferrier@example.com>
RUN apt-get update && apt-get install -y \
        build-essential \
        git \
        gdebi-core
WORKDIR /tmp
COPY . /tmp/cromer/
WORKDIR /tmp/cromer
RUN make builddeb_real && sh -c 'ls -1 /tmp/cromer/*.deb | xargs -L 1 gdebi -n' && cp /tmp/cromer/*.deb /tmp
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*
