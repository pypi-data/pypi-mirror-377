# coding:utf-8
"""
# State Machine for HEROs

This keeps a cache of the last known state of a datasource and
allows to query this cache via a HTTP metrics endpoint. This is
especially useful for scraping from prometheus or influxdb.


 * {observable}_time {return_value.time}
 * {observable}_value {return_value.value}
   if unit is not 'None' a label {unit='{{return_value.unit}}'} is attached
 * {observable}_raw_value {return_value.raw_value}
   if unit is not 'None' a label {unit='{{return_value.raw_unit}}'} is attached

A predefined set of labels is attached to the metrics.
Observable names are cleaned to match metric names [a-z0-9_]
 trailing _ and repetitions _ are removed.

"""

import re
import copy
from aiohttp import web
import time

from heros import DatasourceObserver
from heros.datasource.types import DatasourceReturnSet
from herostools.helper import log
from six import integer_types


no_metric = re.compile(r"[\Wäöüß]")
minify_metric = re.compile(r"__+")
allowed_types = integer_types + (
    float,
    bool,
)


class HERODatasourceStateMachine(DatasourceObserver):
    def __init__(
        self,
        loop,
        *args,
        http_port: int = 9090,
        bind_address: str = "localhost",
        metrics_endpoint="/metrics",
        object_selector: str = "*",
        labels: dict = {},
        **kwargs,
    ):
        """
        An actor to aggregate data from all available datasources and keep a cache that contains the
        last known state.
        A view on the cache is provided in the prometheus data export format. This can be used as a
        target for scraping in prometheus or influxdb.

        Args:
            loop: asyncio event loop to which the webserver gets attached.
            http_port: Port for the HTTP server to run on
        """
        DatasourceObserver.__init__(self, object_selector=object_selector, *args, **kwargs)

        self.cache = {}
        self._http_port = http_port
        self._bind_address = bind_address
        self._metrics_endpoint = metrics_endpoint

        self._global_labels = labels

        self.register_callback(self._update)
        loop.create_task(self._start_webserver())

    async def _http_handle_metrics(self, request):
        text = (
            "\n\n".join(
                [
                    self._convert_to_metrics(return_value_set, prefix=obj_name)
                    for obj_name, return_value_set in self.cache.items()
                ]
            )
            + "\n"
        )
        return web.Response(text=text)

    async def _start_webserver(self):
        app = web.Application()
        app.add_routes([web.get(self._metrics_endpoint, self._http_handle_metrics)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self._bind_address, self._http_port)
        await site.start()

    def _metric_name(self, key):
        """create a clean name for a metric without special characters matching [a-z0-9_]."""
        metric = no_metric.sub("_", key.lower())
        metric = minify_metric.sub("_", metric)
        metric = metric.strip("_")
        return metric

    def _unit_name(self, unit):
        """cleans units to not contain special characters"""
        # according to https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels
        # the values of a label (in this case the value of the label "unit") can contain any
        # Unicode character. However, stuff went havoc when confronted with a µ...

        # it's useful to replace µ with u, e.g. µA -> uA
        out = unit.replace("µ", "u")

        # I don't know what else to clear and want to keep "/", so that's it for now...
        return out

    def _update(self, source_name, data):
        """
        update the values in the cache for source_name
        """
        log.debug(f"updating values received from {source_name}")
        if isinstance(data, DatasourceReturnSet):
            self.cache.update({source_name: data})
        else:
            log.warning(f"data received from {source_name} is not of type DatasourceReturnSet")

    def _convert_to_metrics(self, dsrs: DatasourceReturnSet, prefix=None):
        metrics = []
        for entry in dsrs:
            key = entry.id
            metric = f"{prefix}_{key}" if prefix is not None else key
            metric = self._metric_name(metric)

            # we should not expose metrics that are to far the current timestamp since prometheus will otherwise
            # omit all metrics
            if abs(entry.time - time.time()) > 600:
                continue

            timestamp = int(entry.time * 1000)  # milliseconds since epoch

            labels = copy.copy(self._global_labels)
            labels.update({"prefix": prefix if prefix else ""})
            labels.update({"key": key})
            metrics.append([f"{metric}_inbound", copy.copy(labels), entry.inbound, timestamp])

            if entry.value is not None and isinstance(entry.value, allowed_types):
                log.info(f"setting quantity {prefix}")
                if entry.unit != "None":
                    log.info(f"setting unit for {prefix} to {entry.unit}")
                    labels.update({"unit": self._unit_name(entry.unit)})
                metrics.append([f"{metric}_value", copy.copy(labels), float(entry.value), timestamp])
            if entry.raw_value is not None and isinstance(entry.raw_value, allowed_types):
                if entry.raw_unit != "None":
                    labels.update({"unit": self._unit_name(entry.raw_unit)})
                metrics.append([f"{metric}_raw_value", copy.copy(labels), float(entry.raw_value), timestamp])

        def label_string(labels) -> str:
            if len(labels) > 0:
                return "{" + ",".join([f'{key}="{value}"' for key, value in labels.items()]) + "}"
            else:
                return ""

        log.info(metrics)
        return "\n".join([f"{name}{label_string(labels)} {value} {time}" for name, labels, value, time in metrics])

    def get_cache(self):
        return self.cache

    def clear(self):
        self.cache.clear()


if __name__ == "__main__":
    import asyncio

    log.setLevel("debug")

    loop = asyncio.new_event_loop()

    p = HERODatasourceStateMachine(loop, http_port=9090)

    async def push_loop():
        while True:
            log.info("waiting..")
            await asyncio.sleep(5)

    loop.create_task(push_loop())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop()
        p._session_manager.force_close()
