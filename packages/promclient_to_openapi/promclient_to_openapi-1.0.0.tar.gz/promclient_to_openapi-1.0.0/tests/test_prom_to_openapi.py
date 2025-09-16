"""Tests for promclient_to_openapi."""

import hashlib
import json

from prometheus_client import REGISTRY, Gauge

from promclient_to_openapi import prometheus_client_to_openapi
from promclient_to_openapi.utils import snake_to_pascal

m1 = Gauge(name="test_metric_foo", documentation="Test metric", labelnames=("metric",))
m1.labels(("1",)).set(value=1)

m2 = Gauge(name="test_metric_bar", documentation="Test metric", labelnames=("metric",))
m2.labels(("2",)).set(value=2)


def test_pascalize() -> None:
    """Test converting snake_case to PascalCase."""

    assert snake_to_pascal("test_string_foo_bar") == "TestStringFooBar"


def test_sync_from_text_defaults() -> None:
    """Test default collectors schema generated from metrics text."""

    t = json.dumps(prometheus_client_to_openapi(metrics=REGISTRY)).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "198552cf55c5ede783cbf2ba1819f318"


def test_sync_from_text_custom() -> None:
    """Test default collectors schema generated from metrics text."""

    labels_descriptions: dict[str, str] = {
        "major": "Python major  version number",
        "minor": "Python minor version number",
        "patchlevel": "Python patchlevel version number",
        "implementation": "Python implementation",
        "version": "Python version string",
    }

    t = json.dumps(
        prometheus_client_to_openapi(
            metrics=REGISTRY,
            describe_labels=labels_descriptions,
            description="Customized description",
            property_name="MyCoolMetrics",
        ),
    ).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "35754662d37a6bbb18ca3433b1bffaaa"


def test_sync_from_metrics_defaults() -> None:
    """Test schema generation with dummy metrics."""

    t = json.dumps(prometheus_client_to_openapi(metrics=(m1, m2))).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "b7fe1b9a118b7e1219804fdec77f30a1"


def test_sync_from_metrics_custom() -> None:
    """Test schema generation with dummy metrics."""

    labels_descriptions: dict[str, str] = {"metric": "Test label"}
    t = json.dumps(
        prometheus_client_to_openapi(
            metrics=(m1, m2),
            describe_labels=labels_descriptions,
            description="Customized description",
            property_name="MyCoolMetrics",
        ),
    ).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "fc8659588ba51cb50d7eeebd0b06cd11"
