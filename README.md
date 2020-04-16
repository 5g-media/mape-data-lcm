# Data-Lifecycle-Manager component

This component is part of the 5G-MEDIA MAPE service. Take a look in the [MAPE](https://github.com/5g-media/mape) repository.

## Introduction

This component:
- consumes messages from the `ns` topic (intra-OSM kafka bus, OSM release>3)
- upon NS `terminate` event, remove the existing VDU entries from the Redis
- upon NS `terminated` event, remove the existing series from the InfluxDB database considering the tag `ns_uuid` (disabled by default)

The OSM release 4/5 publishes messages in the topic `ns` using a set of keys such as:
- [x] instantiate
- [x] instantiated
- [x] terminate
- [x] terminated

## Requirements
- Python 3.5+ 
   + a set of python packages are used (see requirements.txt).
- The Apache Kafka broker must be accessible from the component.
- The InfluxDB must be accessible from the component.
- The Redis must be accessible from the component.


## Installation/Deployment

To build the docker image, copy the bash script included in the `bash_scripts/`folder in the parent folder of the project and then, run:
```bash
   chmod +x build_docker_image.sh
   ./build_docker_image.sh
```

Considering the availability of the docker image, you can deploy the component as follows:
```bash
$ sudo docker run -p 8882:3333 --name data_lcm --restart always \
    -e PUBLIC_IP="kafka_ivp4" \
    -e OSM_IP="192.168.1.196" \
    -e OSM_KAFKA_IP="192.168.1.175" \
    -e OSM_KAFKA_PORT="9094" \
    -e OSM_USER="admin" \
    -e OSM_PWD="password" \
    -e REDIS_PORT="6379" \
    -e REDIS_EXPIRATION_SEC="14400" \
    -e KAFKA_PORT="9092" \
    -e INFLUXDB_DB_NAME="monitoring" \
    -e INFLUXDB_USER="root" \
    -e INFLUXDB_PWD="password" \
    -e INFLUXDB_PORT="8086" \
    -dit ns_manager
```

## Usage

Access the docker container:
```bash
$ sudo docker exec -it data_lcm bash
```

Start the NS manager service through the supervisor:
```bash
$ service supervisor start && supervisorctl start data-lcm
```

Stop the service through the supervisor:
```bash
$ supervisorctl stop data-lcm
```

Stop the supervisor service:
```bash
$ service supervisor stop 
```

You are able to see to status of service from browser using the supervisor UI;
type the URL http://{ipv4}:8882.

## Tests
Access the Kafka cli in the running kafka container:
```bash
sudo docker exec -it kafka-docker_kafka_1 bash
```

Run the bash script to produce a message using key:
```bash
$ bin/kafka-console-producer.sh --broker-list <intra-OSM-kafka-ipv4>:9094 --topic ns --property "parse.key=true" --property "key.separator=:"
```

The message should include a key and a value in the format: `key:value`. Check the messages under the folder `samples`.
Consider that these messages are in `JSON` (dict) while the actual one must be `YAML`.

To inspect the keys in the redis, follow the steps assuming that no password is needed:
```bash
$ sudo docker exec -it redis-cache bash
...
# redis-cli -n 0
...
> keys "ocata-devstack:*" // list keys having a pattern
1) "ocata-devstack:9c1bb4ad-1481-4d0f-be7f-a1928a014dfa"
2) "ocata-devstack:6e761377-fad3-46ec-a057-6e82e804d4d5"
3) "ocata-devstack:aa21a181-c3b1-4318-b0f3-df6f2c09b24b"
4) "ocata-devstack:69f9d7d7-c3f0-4cee-b0bd-4113d8c2ac43"
5) "ocata-devstack:47e43530-8a9e-4539-a54c-41dace08193b"
6) "ocata-devstack:65b297f2-de6c-45da-9a1b-8058efcba169"

...
> get "<key>" // get value by given key
"{\"vim\": {\"url\": \"http://192.168.1.147/identity/v3\", \"type\": \"openstack\", \"name\": \"ocata-devstack\", \"uuid\": \"41dab0c0-35f4-4c40-b1cd-13e4a79dab48\"}, \"vnf\": {\"vnfd_id\": \"16c40d2e-7a1b-4f22-9e50-3f7ede3e9fc4\", \"id\": \"a1e94c24-1155-400d-9d28-57ed00da7ea2\"}, \"ns\": {\"nsd_name\": \"cirros_2vnf_ns\", \"name\": \"takis-0007\", \"id\": \"47546676-fbb2-4990-bb3e-ca0b188f0072\", \"nsd_id\": \"d5c99561-ec46-4480-8377-b5b218b8b1e5\"}, \"vdu\": {\"mgmt-interface\": null, \"status\": \"ACTIVE\",  \"name\": \"takis-0007-1-cirros_vnfd-VM-1\", \"id\": \"65b297f2-de6c-45da-9a1b-8058efcba169\", \"ip_address\": \"192.168.157.1\"}}"
...

> mget "<key1>" "<key2>" // get values by given multiple keys
1) "{\"vim\": {\"url\": \"http://192.168.1.147/identity/v3\", \"type\": \"openstack\", \"name\": \"ocata-devstack\", \"uuid\": \"41dab0c0-35f4-4c40-b1cd-13e4a79dab48\"}, \"vnf\": {\"vnfd_id\": \"16c40d2e-7a1b-4f22-9e50-3f7ede3e9fc4\", \"id\": \"a1e94c24-1155-400d-9d28-57ed00da7ea2\"}, \"ns\": {\"nsd_name\": \"cirros_2vnf_ns\", \"name\": \"takis-0007\", \"id\": \"47546676-fbb2-4990-bb3e-ca0b188f0072\", \"nsd_id\": \"d5c99561-ec46-4480-8377-b5b218b8b1e5\"}, \"vdu\": {\"mgmt-interface\": null, \"status\": \"ACTIVE\", \"name\": \"takis-0007-1-cirros_vnfd-VM-1\", \"id\": \"65b297f2-de6c-45da-9a1b-8058efcba169\", \"ip_address\": \"192.168.157.1\"}}"
2) "{\"vnf\": {\"id\": \"5ad8628f-7493-4e92-87e2-5e8646d37a44\", \"vnfd_id\": \"16c40d2e-7a1b-4f22-9e50-3f7ede3e9fc4\"}, \"ns\": {\"nsd_id\": \"d5c99561-ec46-4480-8377-b5b218b8b1e5\", \"id\": \"c19a1f29-4445-45e4-9700-496501876237\", \"nsd_name\": \"cirros_2vnf_ns\", \"name\": \"takis-0006\"}, \"vdu\": {\"status\": \"ACTIVE\", \"ip_address\": \"192.168.49.9\", \"id\": \"47e43530-8a9e-4539-a54c-41dace08193b\", \"mgmt-interface\": null, \"name\": \"takis-0006-2-cirros_vnfd-VM-1\"}, \"vim\": {\"url\": \"http://192.168.1.147/identity/v3\", \"type\": \"openstack\", \"name\": \"ocata-devstack\"}}"
...

> del "<key>" // delete entry by given key
(integer) 1
```
More info about the redis-cli is available [here](https://redis.io/topics/rediscli).

## Authors
- Singular Logic <pathanasoulis@ep.singularlogic.eu>

## Contributors
 - Contact with Authors
 
## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 761699. The dissemination of results herein reflects only the author’s view and the European Commission is not responsible for any use that may be made of the information it contains.

## License
[Apache 2.0](LICENSE.md)


