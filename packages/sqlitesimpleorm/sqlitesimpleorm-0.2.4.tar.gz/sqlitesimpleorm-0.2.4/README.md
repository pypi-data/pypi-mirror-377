# sqlitesimpleorm

A lightweight SQLite ORM for Python.  
Provides a simple interface to define tables, columns, relationships, and perform queries with filtering and joins.

## Features
- Define tables with different column types (`Integer`, `Text`, `Boolean`, `DateTime`, `ForeignKey`).
- Automatic table creation and migration.
- Basic ORM-style query API (`all`, `one`, `insert`, `delete`).
- Filtering with lookups (`exact`, `contains`, `startswith`, `endswith`, `icontains`, `null`, `notnull`).
- Support for `Q` objects to combine complex filters with `AND` / `OR`.
- Support for table joins.

## Installation
```bash
pip install sqlitesimpleorm
```

Quick Example

```
from sqliteorm import SQLiteORM
from sqliteorm.models.table import Table
from sqliteorm.models.fields import IntegerColumn, TextColumn

# Initialize DB
db = SQLiteORM("example.db")

# Define a model
class User(Table):
    id = IntegerColumn("id")
    name = TextColumn("name")

    def __init__(self, db):
        super().__init__(db, "users")

# Register table
users = User(db)
db.add_table(users)

# Insert row
users.insert(name="Alice")

# Query rows
print(users.all())
```

License

MIT License.
See [LICENSE](LICENSE) for details.