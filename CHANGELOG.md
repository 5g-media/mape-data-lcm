# CHANGELOG
---

## 2018-11-28
- Use redis for caching. This service listens the NS events from the intra-OSM-r4 kafka bus (topic `ns`)
and based on the type of the event adds an entry in redis or deletes an existing entry from the redis.

## 2018-07-25
- Delete the series related to a NS UUID from the InfluxDB (on demand) 

