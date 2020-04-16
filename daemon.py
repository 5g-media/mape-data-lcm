import redis
import json
import yaml
import logging.config
from kafka import KafkaConsumer
from influxdb import InfluxDBClient
from utils import convert_byte_to_str, get_vdus_info, compose_redis_key
from exceptions import NsValueIsNotDict, NsUuidDoesNotExist
from settings import KAFKA_SERVER, KAFKA_CLIENT_ID, KAFKA_API_VERSION, KAFKA_NS_MANAGER_TOPIC, INFLUX_DATABASES, \
    REDIS_HOST, REDIS_PORT, REDIS_NFVI_DB, REDIS_EXPIRATION_SECONDS, LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def main():
    # See more: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
    consumer = KafkaConsumer(bootstrap_servers=KAFKA_SERVER, client_id=KAFKA_CLIENT_ID, enable_auto_commit=True,
                             value_deserializer=lambda v: yaml.safe_load(v.decode('utf-8', 'ignore')),
                             api_version=KAFKA_API_VERSION, )
    consumer.subscribe(KAFKA_NS_MANAGER_TOPIC)

    # See more: http://influxdb-python.readthedocs.io/en/latest/examples.html
    influx_client = InfluxDBClient(host=INFLUX_DATABASES['default']['HOST'], port=INFLUX_DATABASES['default']['PORT'],
                                   username=INFLUX_DATABASES['default']['USERNAME'],
                                   password=INFLUX_DATABASES['default']['PASSWORD'],
                                   database=INFLUX_DATABASES['default']['NAME'])

    # See more: https://redis-py.readthedocs.io/en/latest/
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_NFVI_DB)

    # Run each message in "ns" topic
    for message in consumer:
        logger.info(message)
        message_key = convert_byte_to_str(message.key)
        message_value = message.value

        if message_key == "instantiate":
            """
            An indicative sample of message is available in the file `samples/instantiate.json`.
            Since the NS instantiation is still in progress, we skip this info.
            """
            pass

        elif message_key == "instantiated":
            """
            When a new Network Service has successfully instantiated through OSM, a new entry is added in the Redis.
            The Redis is used as a cache to avoid continuous requests in OSM-r4 NBI API in the translation process.
            
            The translator could check if there is info in the redis related to the metric that is under process.
            If there is (`hit` case), then no call in OSM r4 NBI API is needed. In `miss` case, the OSM will be used. 
            
            The key is a composition of <vim_name>:<vdu_uuid>. Use lower function in `vim_name`.
            An indicative sample of message is available in the file `samples/instantiated.json`.
            """
            pass

            # # Get the operational state of the process
            # ns_operation_state = message_value['operationState']
            # if ns_operation_state != 'COMPLETED':
            #     continue
            # ns_uuid = message_value.get('nsr_id', None)
            #
            # # Find the vdus for the new Network Service
            # vdu_records = get_vdus_info(ns_uuid=ns_uuid)
            #
            # # Update the entries in the redis, if needed
            # for vdu_record in vdu_records:
            #     vim_name = vdu_record.get("vim", {}).get('name', None)
            #     if vim_name is None:
            #         continue
            #
            #     vdu_uuid = vdu_record.get("vdu", {}).get('id', None)
            #     if vdu_uuid is None:
            #         continue
            #
            #     # Compose the redis key
            #     redis_key = compose_redis_key(vim_name, vdu_uuid)
            #
            #     # Check if there is value for the given key. If no, insert a value. Otherwise, do nothing.
            #     existing_value = redis_conn.get(name=redis_key)
            #     if existing_value is None:
            #         redis_conn.set(name=redis_key, value=json.dumps(vdu_record), ex=REDIS_EXPIRATION_SECONDS)
            #         logger.info("[Redis] Add key: `{}` with value: `{}`".format(redis_key, vdu_record))

        elif message_key == "terminate":
            """
            In this step, the NS termination is still in progress. However, this the proper time to remove the entries
            from redis since we can retrieve the vim information, since we can invoke the ns-instance web service. 
            
            An indicative sample of message is available in the file `samples/terminate.json`
            """
            ns_uuid = message_value.get('nsInstanceId', None)
            if ns_uuid is None:
                continue

            # Remove the entries related to the `ns_uuid` in Redis.
            vdu_records = get_vdus_info(ns_uuid=ns_uuid)
            for vdu_record in vdu_records:
                vim_name = vdu_record.get("vim", {}).get('name', None)
                if vim_name is None:
                    continue
                vdu_uuid = vdu_record.get("vdu", {}).get('id', None)
                if vdu_uuid is None:
                    continue

                # Check if there are keys with the pattern: *:{vdu_uuid}.
                # If yes, delete the relevant entry. Otherwise, do nothing.
                vdu_keys = redis_conn.keys(pattern="*:{}".format(vdu_uuid))
                vtranscoder_keys = redis_conn.keys(pattern="*_metrics:*")
                spectator_keys = redis_conn.keys(pattern="spectators.vtranscoder3d.metrics:transcoder*")
                matched_keys = vdu_keys + vtranscoder_keys + spectator_keys
                for k in matched_keys:
                    existing_value = redis_conn.get(name=k)
                    if existing_value is not None:
                        redis_conn.delete(k)
                        logger.info("[Redis] Delete key: `{}`".format(k))

        elif message_key == "terminated":
            """           
            When a new Network Service is terminated through OSM, delete the data from `InfluxDB` and the Redis. 
            The key is a composition of <vim_name>:<vdu_uuid>.
            
            An indicative sample of message is available in the file `samples/terminated.json`
            """
            # Get the operational state of the process
            ns_operation_state = message_value['operationState']
            if ns_operation_state != 'COMPLETED':
                continue

            # Delete the relevant redis entries
            spectator_keys = redis_conn.keys(pattern="spectators.vtranscoder3d.metrics:transcoder*")
            spectator_vnf_keys = redis_conn.keys(pattern="spectators.vtranscoder3d.metrics:vnf*")
            matched_keys = spectator_keys + spectator_vnf_keys
            for k in matched_keys:
                existing_value = redis_conn.get(name=k)
                if existing_value is not None:
                    redis_conn.delete(k)
                    logger.info("[Redis] Delete key: `{}`".format(k))

            ns_uuid = message_value.get('nsr_id', None)
            if ns_uuid is None:
                continue

            # # Remove the series with the "ns_uuid" tag from the Influxdb
            # try:
            #     logger.info("[InfluxDB] Delete series with tag `ns_uuid`={}".format(ns_uuid))
            #     influx_client.delete_series(database=INFLUX_DATABASES['default']['NAME'], tags={'ns_uuid': ns_uuid})
            # except (NsValueIsNotDict, NsUuidDoesNotExist, Exception) as exc:
            #     logger.exception(exc)

        elif message_key == "action":
            "Future usage"
            pass
        elif message_key == "show":
            "Future usage"
            pass
        elif message_key == "deleted":
            "Future usage"
            pass


if __name__ == '__main__':
    main()
