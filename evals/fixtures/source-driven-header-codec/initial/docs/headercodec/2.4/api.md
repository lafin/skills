# HeaderCodec 2.4 API reference

Snapshot of the HeaderCodec maintainers' versioned reference.
Canonical source: https://docs.example.invalid/headercodec/2.4/api.html
Applies to: HeaderCodec 2.4.x

## `encode_component`

```python
encode_component(value: str, *, separator: str = "_") -> str
```

`encode_component` applies Unicode NFKC normalization, case-folds text, trims
outer whitespace, removes empty components, and joins components with
`separator`. Pass `separator="-"` for cache keys that use hyphens.

The pre-2.0 `legacy_slug` alias is not available in HeaderCodec 2.4.
