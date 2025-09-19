===========================
HEROS Datasource Aggregator
===========================

The HEROS datasource aggregator absorbs the observables coming from all (or a subset) of datasource HEROs in the network and
keeps a cache of the last received value along with its timestamp.

The aggregator runs a webserver that allows to export values in the cache in the prometheus metrics format that can be
scraped by prometheus and influxdb (and maybe more).

.. _Setup:

Setup
*****

This describes the configuration to run the datasource aggregator, prometheus and grafana in a docker compose stack. Of course
it can very well also be run on a bare metal machine. You just need to have heros, boss, and herostools installed in your environment

To pull up the required services, the following docker compose is sufficient:

.. code:: yaml

    volumes:
      prometheus_config:
        driver: local
        name: prometheus_config
      prometheus_data:
        driver: local
        name: prometheus_data
      grafana_data:
        driver: local
        name: grafana_data

    services:
      statemachine-service:
        image: registry.gitlab.com/atomiq-project/herostools
        restart: always
        network_mode: host
        hostname: statemachine
        ports:
          - 9099:9099
        environment:
          - >
            BOSS1=

            {
              "_id": "statemachine",
              "classname": "herostools.actor.statemachine.HERODatasourceStateMachine",
              "arguments": {
                "loop": "@_boss_loop",
                "http_port": 9099,
                "bind_address": "0.0.0.0",
                "labels": {"system": "heros"}
              }
            }
        command: python -m boss.starter -e BOSS1 --name boss-statemachine

      prometheus:
        image: prom/prometheus:latest
        restart: unless-stopped
        container_name: prometheus
        command:
          - --config.file=/etc/prometheus/prometheus.yml
          - --storage.tsdb.retention.time=10y
        volumes:
          - prometheus_config:/etc/prometheus
          - prometheus_data:/prometheus

      grafana:
        image: grafana/grafana:latest
        container_name: grafana
        restart: unless-stopped
        ports:
          - 3000:3000
        volumes:
          - grafana_data:/var/lib/grafana
        depends_on:
          - prometheus


You have to add an entry to your prometheus `scrape_config` section as follows:

.. code:: yaml

    scrape_configs:
    - job_name:       'heros-datasources'
        scrape_interval: 5s
        metrics_path: /metrics
        static_configs:
        - targets: ['172.17.0.1:9099']
            labels:
            group: 'heros'

The target IP 172.17.0.1 given here targets the docker host, which is required since the aggregator runs in the host network


Other Database Backends
***********************

Influx DB
---------
In the docker compose file :ref:`above<Setup>`, you have to remove the `prometheus` service and instead add services running
`influxdb` and `telegraf`.

`Telegraf <https://www.influxdata.com/time-series-platform/telegraf/>`_ can directly ingest from the `/metrics` endpoint, by adding

.. code:: toml

    [[inputs.prometheus]]
      urls = ["http://172.17.0.1:9099/metrics"]

to your Telegraf configuration file. Then configure the output to your influxdb as described in the InfluxDB documentation.

Quest DB
--------
`QuestDB <https://questdb.com/>`_ is a time series database that uses SQL. Telegraf can be used to scrape the `/metrics` endpoint.
In the docker compose file :ref:`above<Setup>`, you have to remove the `prometheus` service and instead add services running
`questdb` and `telegraf`.

The following Telegraf configuration writes the metrics into the QuestDB:

.. code:: toml

  [[outputs.influxdb_v2]]
    # Use InfluxDB Line Protocol to write metrics to QuestDB
    urls = ["http://questdb:9000"]
    # Disable gzip compression
    content_encoding = "identity"

  # Heros statemachine
  [[inputs.prometheus]]
    urls = ["http://172.17.0.1:9099/metrics"]
    metric_version = 2 # all entries will be on a single table
    ignore_timestamp = false

Since QuestDB has a slightly different structure than Prometheus or InfluxDB, it makes sense to split up the metrics into multiple databases
based on the device (or `prefix`) they are coming from. Add the following code to your telegraf config:

.. code:: toml

  [[processors.starlark]]
    source = '''
  def apply(metric):
    # Extract the prefix from the tags
    if metric.name == "prometheus":
      prefix = metric.tags.get("prefix", "default_prefix")
      if "key" in metric.tags:
        metric.tags.pop("key")
      metric.name = prefix
    return metric
    '''
  [[aggregators.merge]]
    drop_original = true
