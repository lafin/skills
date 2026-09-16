# QueryShape 3.1 parsing reference

Snapshot of the QueryShape maintainers' versioned reference.
Canonical source: https://docs.example.invalid/queryshape/3.1/parsing.html
Applies to: QueryShape 3.1.x

## `iter_pairs`

```python
iter_pairs(query: str, *, keep_blank_values: bool = False)
```

The iterator yields decoded `(name, value)` pairs in input order. Repeated names
remain separate. Set `keep_blank_values=True` when empty values are meaningful.
Names and values use form decoding, including conversion of `+` to a space.

The mapping helper `parse_map` was removed before QueryShape 3.1 because a
mapping cannot preserve every repeated field in source order.
