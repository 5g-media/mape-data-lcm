FROM ubuntu:16.04
MAINTAINER Athanasoulis Panagiotis
LABEL version="1.0"

ENV PUBLIC_IP=$PUBLIC_IP
ENV OSM_IP=$OSM_IP
ENV OSM_USER=$OSM_USER
ENV OSM_PWD=$OSM_PWD
ENV OSM_KAFKA_IP=$OSM_KAFKA_IP
ENV OSM_KAFKA_PORT=$OSM_KAFKA_PORT
ENV REDIS_PORT=$REDIS_PORT
ENV REDIS_EXPIRATION_SEC=$REDIS_EXPIRATION_SEC
ENV INFLUXDB_DB_NAME=$INFLUXDB_DB_NAME
ENV INFLUXDB_USER=$INFLUXDB_USER
ENV INFLUXDB_PWD=$INFLUXDB_PWD
ENV INFLUXDB_PORT=$INFLUXDB_PORT

RUN pwd
RUN apt-get update

# Install required packages
RUN apt-get -y install build-essential apt-utils acl cron libxml2-dev python3-pip vim supervisor htop wget
RUN apt-get -y install python3-dev python3-lxml python3-cffi

# Copy source code
RUN mkdir /opt/data-lcm
COPY data-lcm /opt/data-lcm
RUN ls -la /opt/data-lcm
ADD data-lcm/deployment/data-lcm.conf /etc/supervisor/conf.d/data-lcm.conf

RUN pip3 install -r /opt/data-lcm/requirements.txt

# Configure Supervisor
RUN rm -rf /etc/supervisor/supervisord.conf && \
 cp /opt/data-lcm/deployment/supervisor/supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 3333

# Run script
CMD bash /opt/data-lcm/deployment/run.sh