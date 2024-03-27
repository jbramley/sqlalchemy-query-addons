# TODO
## Smartjoins
 * Handle aliases correctly
 * Allow explicitly specifying inner/outer
 * Prevent double-joins

## Annotations
 * All of this

## Overall
 * Create version of `select` that takes extra keyword arguments to determine which decorators to apply to `Select` e.g.:
```python
query = select(Author, smartjoins=True, annotations=True)
```
