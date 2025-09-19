# coding:utf-8
"""
# Prometheus Actor

Use a prometheus push-gateway as target for prometheus scrape target.

    docker pull prom/pushgateway
    docker run -p 9091:9091 prom/pushgateway

A PrometheusActor aggregates data from labsurveillance
and pushes on Timeout to a prometheus push gateway.
Thereby observables are exposed as metrics

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

import requests

from heros import DatasourceObserver
from herostools.helper import log
from six import iteritems, integer_types


no_metric = re.compile(r"[\Wäöüß]")
minify_metric = re.compile(r"__+")
allowed_types = integer_types + (
    float,
    bool,
)


class PrometheusActor(DatasourceObserver):
    def __init__(self, *args, metrics_path="http://localhost:9091/metrics", labels=dict(job="labsuv"), **kwargs):
        """
        An actor to cache and push date to a prometheus push gateway.

        :param metrics_path: (str) path to pushgateway metrics
        :param labels: (dict<str, str>) a dictionary with additional labels.
        """
        DatasourceObserver.__init__(self, object_selector="*", *args, **kwargs)

        metrics_path = metrics_path.strip("/")
        metrics_path = metrics_path if metrics_path.endswith("/metrics") else "%s/metrics" % metrics_path
        metrics_path = metrics_path if metrics_path.startswith("http") else "http://%s" % metrics_path
        self.metrics_path = metrics_path
        self.labels = labels
        self.path = "/".join(
            "%s/%s" % (self._metric_name(label), self._metric_name(value)) for label, value in iteritems(labels)
        )
        self.cache = {}
        self._session = None

        self.register_callback(self.update)

    def _ensure_session(self):
        if self._session is None:
            self._session = requests.Session()
        return self._session

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

    def update(self, source_name, data):
        """convert a labsuv data dictionary to values"""
        log.debug(f"updating values received from {source_name}")

        for entry in data:
            key = entry.id
            metric = self._metric_name(key)
            self.cache["%s_inbound" % metric] = entry.inbound
            self.cache["%s_time" % metric] = entry.time
            if entry.value is not None and isinstance(entry.value, allowed_types):
                key = "%s_value" % metric
                if entry.unit != "None":
                    key += '{unit="%s"}' % (self._unit_name(entry.unit),)
                self.cache[key] = float(entry.value)
            if entry.raw_value is not None and isinstance(entry.raw_value, allowed_types):
                key = "%s_raw_value" % metric
                if entry.raw_unit != "None":
                    key += '{unit="%s"}' % (self._unit_name(entry.raw_unit),)
                self.cache[key] = float(entry.raw_value)

    def clear(self):
        self.cache.clear()

    def push(self):
        """push current buffer to pushgateway."""
        if not self.cache:
            log.debug("PrometheusActor has nothing to push.")
            return
        data = "\n".join("%s %s" % (k, v) for k, v in iteritems(self.cache))
        data += "\n"
        self.clear()
        url = "/".join((self.metrics_path, self.path))
        request = requests.Request(method="POST", url=url, data=data, headers={"Content-Type": "text"})
        prep = request.prepare()

        session = self._ensure_session()
        result = session.send(prep)
        assert result.status_code < 300, "Cannot push data to %s due to %s \n %s " % (
            url,
            result.status_code,
            result.content,
        )


if __name__ == "__main__":
    import asyncio

    log.setLevel("debug")

    loop = asyncio.new_event_loop()

    p = PrometheusActor(metrics_path="127.0.0.1:9091")

    async def push_loop():
        while True:
            p.push()
            await asyncio.sleep(5)

    loop.create_task(push_loop())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop()
        p._session_manager.force_close()

    # data = dict(test=ReturnValue(value=1, unit="K"))
    # p(data)
    # p.push()
