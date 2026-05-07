---
marp: true
theme: default
paginate: true
---

# Sentinel Values
## Python Lisbon Meetup

**Anže Pečar**
May 7, 2026

---

## A token

```python
@dataclass
class Token:
    value: str                    # always a string
    expires_at: datetime | None   # None means "never expires"
```
---

## Update it

```python
token = Token(value="hi", expires_at=datetime.now())
update(token, expires_at=datetime.now()) # value not updated
update(token, value="new_value")         # expires_at not updated
```

---

## Update it

```python
def update(
    token: Token,
    value: str | None = None,
    expires_at: datetime | None = None,
) -> None:
    if value is not None:
        token.value = value
    if expires_at is not None:
        token.expires_at = expires_at
```

---

`value` is fine — `None` can't be a `str`, so it safely means "keep" existing value.

`expires_at` is broken:

```python
update(t, expires_at=None)   # "never expires"? or "keep" existing value?
```

---

## The old trick

```python
_KEEP = object()

def update(
    token: Token,
    value: str | None = None,
    expires_at: datetime | None | object = _KEEP,  # 🤮
) -> None:
    if value is not None:
        token.value = value
    if expires_at is not _KEEP:
        token.expires_at = expires_at
```

---

`object` type annotations accepts *anything*. And:

```python
>>> _KEEP
<object object at 0x10a3f2b40>
```

Ugly repr, no real type, breaks on pickle.

---

## PEP 661 - Python 3.15a8

```python

KEEP = sentinel('KEEP')

```

---

## PEP 661 - Python 3.15a8

```python

KEEP = sentinel('KEEP')

def update(
    token: Token,
    value: str | KEEP = KEEP,
    expires_at: datetime | None | KEEP = KEEP,
) -> None:
    if value is not KEEP:
        token.value = value
    if expires_at is not KEEP:
        token.expires_at = expires_at
```

---

Clean repr. No issues with type annotation. Survives pickling.

---

## Thank you!

`peps.python.org/pep-0661`
