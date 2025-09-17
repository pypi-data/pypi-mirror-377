## manifold_fabric_utils

Utilities for Microsoft Fabric/Spark environments, with helpers for working with Lakehouse `Tables/` and `Files/` using `notebookutils.mssparkutils`.

### Install

```bash
pip install .
```

Requires Python 3.6+ and a Fabric/Spark runtime for functions that call `mssparkutils`.

### Quick start

```python
from manifold_fabric_utils import (
    path_exists,
    list_dir,
    map_dir,
    create_schema_if_not_exists,
)

# Works with local/posix paths and Fabric Lakehouse paths
path_exists("/tmp")               # True/False via os.path.exists
path_exists("Tables/my_schema")   # Uses mssparkutils.fs.ls under the hood

# Directory listing (Lakehouse path expected for list/map helpers)
files = list_dir("Files/my_folder")        # List[str]
names_iter = map_dir("Files/my_folder")    # Iterator[str]

# Create a Lakehouse schema folder if missing
created = create_schema_if_not_exists("my_schema")  # True if created, else False
```

### API

- **path_exists(path)**: Returns True if a local path exists or if a Lakehouse path (`Tables/` or `Files/`) can be listed via `mssparkutils.fs.ls`.
- **list_dir(path)**: Returns a list of entry names for a Lakehouse directory.
- **map_dir(path)**: Returns an iterator of entry names for a Lakehouse directory.
- **create_schema_if_not_exists(schema_name)**: Ensures `Tables/{schema_name}` exists; creates it if missing.

### Notes

- Functions that touch `Tables/` and `Files/` require `notebookutils.mssparkutils` (Fabric/Spark environment).
- Local filesystem behavior uses the standard library (`os.path`).

### License

MIT


