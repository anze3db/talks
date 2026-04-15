---
marp: true
theme: default
paginate: false
---

# Speeding Up Django Startup Times with Lazy Imports

**Anže Pečar**
DjangoCon Europe 2026

---

## Imports in Python can be slow

---

<!-- _backgroundColor: black -->
<video src="assets/lazy-imports.mov" autoplay muted loop style="width:100%;height:100%;object-fit:contain;"></video>

---

```bash
python -X importtime ./manage.py check
```

```
  Slowest imports by self time (all levels):

     self  cumulative  package
  ───────────────────────────────────────────────────────────────────────────────────
  783.5ms       2.30s  google.cloud.asset_v1
  965.7ms     978.9ms  google.pubsub_v1
  720.1ms     767.2ms  google.cloud.osconfig_v1
  709.9ms     710.4ms  google.api_core
  661.7ms     725.0ms  google.cloud.orgpolicy_v2
  332.8ms     498.5ms  google.cloud.monitoring_v3
  144.8ms     146.1ms  google.cloud.monitoring_v3.services.group_service.async_client
  129.5ms     129.5ms  snowflake.core.network_policy._generated.models.tag_reference
  115.2ms     115.2ms  apps.integrations.gcp.datastructures
```

---

## Existing code

```python
from google.cloud.storage import Client as StorageClient

def get_storage_client() -> StorageClient:
      return StorageClient(...)
```

---

## Lazy code

```python
if TYPE_CHECKING:
    from google.cloud.storage import Client as StorageClient

def get_storage_client() -> StorageClient:
      from google.cloud.storage import Client as StorageClient
      return StorageClient(...)
```

---

## Lazy code

```python

def get_storage_client_1():
      from google.cloud.storage import Client as StorageClient
      return StorageClient(...)

def get_storage_client_2():
      from google.cloud.storage import Client as StorageClient
      return StorageClient(...)

def get_storage_client_3():
      from google.cloud.storage import Client as StorageClient
      return StorageClient(...)
```

---

## From 13s to 3s

<table>
  <thead><tr><th>Metric</th><th style="text-align: right;">Value</th></tr></thead>
  <tbody>
    <tr><td>Files changed</td><td style="text-align: right;">130</td></tr>
    <tr style="color: green;"><td>Lines added</td><td style="text-align: right;">1,125</td></tr>
    <tr style="color: red;"><td>Lines deleted</td><td style="text-align: right;">547</td></tr>
    <tr><td><b>Net lines added</b></td><td style="text-align: right;"><b>578</b></td></tr>
  </tbody>
</table>

---

## PEP 810 (Python 3.15) 😍

---

## Lazy import

```python
lazy from google.cloud.storage import Client as StorageClient

def get_storage_client() -> StorageClient:
      return StorageClient(...)
```

---

## Super lazy import

```bash
python -X lazy_imports=all
```

```python
from google.cloud.storage import Client as StorageClient

def get_storage_client() -> StorageClient:
      return StorageClient(...)
```
---

## Be Lazy!

---

## 🤫 Lazy imports also allow circular imports

```python
# a.py
lazy from .b import B

class A:
    def get_b(self):
        return B(self)
```

```python
# b.py
lazy from .a import A

class B:
    def get_a(self):
        return A(self)
```
✅ This now imports without errors
