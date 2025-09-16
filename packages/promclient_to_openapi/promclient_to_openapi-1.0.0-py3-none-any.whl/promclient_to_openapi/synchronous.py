"""Translates prometheus_client metrics to OpenAPI."""

from collections.abc import Iterable
from typing import Any

from prometheus_client import generate_latest
from prometheus_client.metrics import MetricWrapperBase
from prometheus_client.metrics_core import Metric
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.registry import CollectorRegistry

from promclient_to_openapi.utils import snake_to_pascal


def prometheus_client_to_openapi(
    metrics: CollectorRegistry | Iterable[MetricWrapperBase],
    describe_labels: dict[str, str] | None = None,
    property_name: str = "PrometheusClientMetrics",
    description: str = "Prometheus-compatible metrics",
) -> dict[str, Any]:
    """
    Produce OpenAPI schema from prometheus_client library.

    If metrics argument is registry, this will collect the actual metrics and
    parse text back. Suitable when various collectors are used.

    If metrics argument is list of metrics (like `Gauge`, `Counter`, `Info`,
    etc), no metric generation will be invoked.

    Args:
        metrics: Collector registry to generate metrics or list of actual metrics objects.
        describe_labels: Mapping of labels description (case-insensitive).
        property_name: Main property name.
        description: Main property description.

    Returns:
        Dictionary of schema to be converted to OpenAPI JSON.
    """

    if describe_labels is None:
        labels_descriptions = {}

    else:
        labels_descriptions = describe_labels.copy()
        for key in describe_labels:
            labels_descriptions[key.lower()] = describe_labels[key]

    schemas: dict[str, Any] = {
        property_name: {
            "properties": {},
            "type": "object",
            "required": [],
            "title": property_name,
            "description": description,
        },
    }

    if isinstance(metrics, CollectorRegistry):
        text = generate_latest(registry=metrics).decode(encoding="utf-8")
        families = text_string_to_metric_families(text=text)

    else:
        families = metrics

    for metric in families:
        if isinstance(metric, Metric):
            metric_name_pascalized = snake_to_pascal(metric.name)
            metric_name = metric.name
            metric_description = metric.documentation
            metric_labels_names = metric.samples[0].labels.keys()

        elif isinstance(metric, MetricWrapperBase):  # pyright: ignore[reportUnnecessaryIsInstance]
            metric_name_pascalized = snake_to_pascal(metric._name)  # pyright: ignore[reportPrivateUsage, reportUnknownArgumentType, reportUnknownMemberType]  # noqa: SLF001
            metric_name: str = metric._name  # pyright: ignore[reportUnknownVariableType, reportPrivateUsage, reportUnknownMemberType]  # noqa: SLF001
            metric_description = metric._documentation  # pyright: ignore[reportPrivateUsage] # noqa: SLF001
            metric_labels_names: Iterable[str] = metric._labelnames  # pyright: ignore[reportPrivateUsage, reportUnknownMemberType, reportUnknownVariableType]  # noqa: SLF001

        else:
            msg = f"Unknown metric type: {type(metric)}"
            raise NotImplementedError(msg)

        schemas[property_name]["properties"][metric_name] = {
            "$ref": f"#/components/schemas/{metric_name_pascalized}",
        }

        schemas[property_name]["required"].append(metric_name)
        schemas[metric_name_pascalized] = {
            "properties": {},
            "type": "object",
            "title": metric_name_pascalized,
            "description": metric_description,
            "required": [],
        }

        label_name: str
        for label_name in metric_labels_names:  # pyright: ignore[reportUnknownVariableType]
            schemas[metric_name_pascalized]["properties"][label_name] = {
                "type": "string",
                "title": label_name.capitalize(),  # pyright: ignore[reportUnknownMemberType]
            }

            if label_name.lower() in labels_descriptions:  # pyright: ignore[reportUnknownMemberType]
                schemas[metric_name_pascalized]["properties"][label_name]["description"] = labels_descriptions[label_name]

            schemas[metric_name_pascalized]["required"].append(label_name)

        # Should not have fewer than 1 items.
        if not schemas[metric_name_pascalized]["required"]:
            schemas[metric_name_pascalized].pop("required")

    return schemas
