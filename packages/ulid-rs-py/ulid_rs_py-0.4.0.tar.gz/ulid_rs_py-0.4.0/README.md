# ulid-rs-py

[![Package version](https://img.shields.io/pypi/v/ulid-rs-py?color=%2334D058&label=pypi%20package)](https://pypi.org/project/ulid-rs-py/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/ulid-rs-py.svg?color=%2334D058)](https://pypi.org/project/ulid-rs-py/)

Python wrapper for Rust [ulid](https://github.com/dylanhart/ulid-rs) crate

---

## Installation

```bash
pip install ulid-rs-py
```

---

## Quickstart

```python
import uuid
from datetime import datetime, timezone
from ulid import new, from_uuid, from_parts, from_timestamp, from_datetime, from_string, PyUlid

# Generate ulid
py_ulid: PyUlid = new()
print(py_ulid)
print(py_ulid.str())
print(py_ulid.bytes())
print(py_ulid.increment())
print(py_ulid.randomness())
print(py_ulid.timestamp())

# From string
str_value = "01H6D6M1HWY1KNND0FKB8PRR87"
py_ulid = from_string(str_value)
print(py_ulid.str())
assert py_ulid.str() == str_value
assert py_ulid.randomness() + 1 == py_ulid.increment().randomness()

# From uuid
uuid_value = "771a3bce-02e9-4428-a68e-b1e7e82b7f9f"
ulid_value = "3Q38XWW0Q98GMAD3NHWZM2PZWZ"
py_ulid = from_uuid(uuid.UUID(uuid_value))
print(py_ulid.str())
assert py_ulid.str() == ulid_value

# From timestamp
timestamp_value = datetime(2023, 7, 28).timestamp()
py_ulid = from_timestamp(timestamp_value)
print(py_ulid.str())
print(py_ulid.timestamp())
assert py_ulid.timestamp() == timestamp_value
print(py_ulid.randomness())

# From datetime
datetime_value = datetime(2023, 7, 28, hour=1, minute=20, tzinfo=timezone.utc)
py_ulid = from_datetime(datetime_value)
assert py_ulid.str()
assert py_ulid.datetime() == datetime(2023, 7, 28, hour=1, minute=20)
assert py_ulid.timestamp() == datetime_value.timestamp()

# From parts
datetime_value = datetime(2023, 7, 28)
py_ulid_tt = from_timestamp(datetime_value.timestamp())
py_ulid = from_parts(py_ulid_tt.timestamp(), py_ulid_tt.randomness())
assert py_ulid.str() == py_ulid_tt.str()

```

---

## Benchmarks
For details, see [benchmark](https://github.com/rp-libs/ulid-rs-py/blob/main/tests/benchmarks/README.md).
