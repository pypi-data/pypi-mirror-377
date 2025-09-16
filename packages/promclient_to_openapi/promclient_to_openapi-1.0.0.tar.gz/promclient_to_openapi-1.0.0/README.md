Generate OpenAPI components schema from [`prometheus_client`](https://pypi.org/project/prometheus-client/) metrics.

## Install

```bash
pip install promclient_to_openapi
```

## Usage

```python
import json

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from promclient_to_openapi import prometheus_client_to_openapi
from prometheus_client import REGISTRY


app = FastAPI()
metrics_schema = prometheus_client_to_openapi(metrics=REGISTRY)


def custom_openapi():
    """Modify default OpenAPI spec for metrics to be documented."""

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(title="Customized OpenAPI", version="0.1.0", routes=app.routes)
    openapi_schema["components"] = {"schemas": metrics_schema}

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

See more about OpenAPI customization for FastAPI on the [docs](https://fastapi.tiangolo.com/how-to/extending-openapi/).

Or you can provide your list of metrics objects (`Gauge`, `Counter`, `Info`, etc) instead of invoking full metrics generation and parsing and also customize description, root property name and describe labels:

```python

m1 = Gauge(name="test_metric_foo", documentation="Test metric", labelnames=("metric",))
m1.labels(("1",)).set(value=1)

m2 = Gauge(name="test_metric_bar", documentation="Test metric", labelnames=("metric",))
m2.labels(("2",)).set(value=2)

labels_descriptions: dict[str, str] = {"metric": "Test label"}

metrics_schema = prometheus_client_to_openapi(
    metrics=(m1, m2),
    describe_labels=labels_descriptions,
    description="Customized description",
    roperty_name="MyCoolMetrics"
)
```

First example will generate default valid OpenAPI schema extended with default `prometheus_client` metrics definitions:

```yaml
openapi: 3.1.0
info:
  title: Customized OpenAPI
  version: 0.1.0
paths: {}
components:
  schemas:
    PrometheusClientMetrics:
      properties:
        python_gc_objects_collected:
          $ref: '#/components/schemas/PythonGcObjectsCollected'
        python_gc_objects_uncollectable:
          $ref: '#/components/schemas/PythonGcObjectsUncollectable'
        python_gc_collections:
          $ref: '#/components/schemas/PythonGcCollections'
        python_info:
          $ref: '#/components/schemas/PythonInfo'
        process_virtual_memory_bytes:
          $ref: '#/components/schemas/ProcessVirtualMemoryBytes'
        process_resident_memory_bytes:
          $ref: '#/components/schemas/ProcessResidentMemoryBytes'
        process_start_time_seconds:
          $ref: '#/components/schemas/ProcessStartTimeSeconds'
        process_cpu_seconds:
          $ref: '#/components/schemas/ProcessCpuSeconds'
        process_open_fds:
          $ref: '#/components/schemas/ProcessOpenFds'
        process_max_fds:
          $ref: '#/components/schemas/ProcessMaxFds'
      type: object
      required:
        - python_gc_objects_collected
        - python_gc_objects_uncollectable
        - python_gc_collections
        - python_info
        - process_virtual_memory_bytes
        - process_resident_memory_bytes
        - process_start_time_seconds
        - process_cpu_seconds
        - process_open_fds
        - process_max_fds
      title: PrometheusClientMetrics
      description: Prometheus-compatible metrics
    PythonGcObjectsCollected:
      properties:
        generation:
          type: string
          title: Generation
      type: object
      title: PythonGcObjectsCollected
      description: Objects collected during gc
      required:
        - generation
    PythonGcObjectsUncollectable:
      properties:
        generation:
          type: string
          title: Generation
      type: object
      title: PythonGcObjectsUncollectable
      description: Uncollectable objects found during GC
      required:
        - generation
    PythonGcCollections:
      properties:
        generation:
          type: string
          title: Generation
      type: object
      title: PythonGcCollections
      description: Number of times this generation was collected
      required:
        - generation
    PythonInfo:
      properties:
        implementation:
          type: string
          title: Implementation
        major:
          type: string
          title: Major
        minor:
          type: string
          title: Minor
        patchlevel:
          type: string
          title: Patchlevel
        version:
          type: string
          title: Version
      type: object
      title: PythonInfo
      description: Python platform information
      required:
        - implementation
        - major
        - minor
        - patchlevel
        - version
    ProcessVirtualMemoryBytes:
      properties: {}
      type: object
      title: ProcessVirtualMemoryBytes
      description: Virtual memory size in bytes.
    ProcessResidentMemoryBytes:
      properties: {}
      type: object
      title: ProcessResidentMemoryBytes
      description: Resident memory size in bytes.
    ProcessStartTimeSeconds:
      properties: {}
      type: object
      title: ProcessStartTimeSeconds
      description: Start time of the process since unix epoch in seconds.
    ProcessCpuSeconds:
      properties: {}
      type: object
      title: ProcessCpuSeconds
      description: Total user and system CPU time spent in seconds.
    ProcessOpenFds:
      properties: {}
      type: object
      title: ProcessOpenFds
      description: Number of open file descriptors.
    ProcessMaxFds:
      properties: {}
      type: object
      title: ProcessMaxFds
      description: Maximum number of open file descriptors.
```

## TODO

- Add [`aioprometheus`](https://pypi.org/project/aioprometheus/) support
