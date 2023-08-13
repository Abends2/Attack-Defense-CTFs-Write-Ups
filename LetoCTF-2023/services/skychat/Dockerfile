FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y netcat build-essential python3 libboost-dev libpq-dev

ADD ./libpqxx-7.7.5.tar.gz /opt
WORKDIR /opt/libpqxx-7.7.5
RUN ./configure
RUN make
RUN make install

COPY ./app /app
WORKDIR /app
RUN g++ main.cpp -lpthread -lpqxx -lpq -I/app -o app

COPY ./entry.sh /app
RUN chmod +x ./entry.sh
CMD ./entry.sh
