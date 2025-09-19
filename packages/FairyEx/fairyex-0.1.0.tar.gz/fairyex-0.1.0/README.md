# FairyEx

FairyEx (for FEE Extraction) is a Python package to perform extraction with some ZIP solution file.


## Magical extraction

- Fast: up to more than 10 times for big extraction
- Efficient: low memory usage
- Easy: to install and to use


## Quickstart

```python
from fairyex import DarkSol

with DarkSol("Model Open World Solution.zip") as ds:
    df = ds.query(
        phase="STSchedule",
        children_class="Generator",
        children=ds.query_children("Generator"),
        properties=["Generation"],
        samples=["1", "2", "3"],
    )
```
