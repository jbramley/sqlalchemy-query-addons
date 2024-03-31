# TODO
## Smartjoins
 * Handle aliases correctly
 * Allow explicitly specifying inner/outer
 * Prevent double-joins
 * Support all join types listed in the docs: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#joins
   * [ ] Joins to a Target Entity
   * [ ] Relationships with custom ON criteria
   * [ ] Joining to subqueries
   * [ ] select_from()


## Annotations
 * All of this

## Overall
 * Create version of `select` that takes extra keyword arguments to determine which decorators to apply to `Select` e.g.:
```python
query = select(Author, smartjoins=True, annotations=True)
```
