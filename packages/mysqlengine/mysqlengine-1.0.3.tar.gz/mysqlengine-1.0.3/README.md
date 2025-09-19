## A Cython-Accelerated, Pythonic MySQL ORM & Query Builder

Created to be used in a project, this package is published to github for ease of management and installation across different modules.

## Installation

Install from `PyPi`

```bash
pip install mysqlengine
```

Install from `github`

```bash
pip install git+https://github.com/AresJef/MysqlEngine.git
```

## Requirements

- Python 3.10 or higher.
- MySQL 5.5 or higher.

## Features

MysqlEngine is a Python/Cython hybrid library that provides a high-performance, programmatic interface to MySQL. It provides:

- An ORM-style schema definition via <'Database'>, <'Table'>, <'Column'>, etc.
- A fluent query-builder (less hand-written SQL strings).
- Built-in support for both sync and async workflows.
- Custom <'TimeTable'> class to create and manage time-series partitions.
- Critical parts are implemented in Cython, minimizing Python overhead and maximizing throughput.

MysqlEngine is built on top of [SQLCyCli](https://github.com/AresJef/SQLCyCli). Because SQLCyCli already delivers solid and high-performance connectivity, MysqlEngine can concentrate on its higher-level features.

- Delegates raw socket I/O, packet parsing, authentication, pooling, and cursor management to SQLCyCli.
- All exeption is inherited from the `SQLCyCli.errors.MySQLError`.

## Example (Normal Table)

```python
import asyncio
from mysqlengine import Database, Table, Pool
from mysqlengine import Column, Index, Define, PrimaryKey


# Difine Table
class User(Table):
    id: Column = Column(Define.BIGINT(unsigned=True, auto_increment=True))
    name: Column = Column(Define.VARCHAR(255))
    pk: PrimaryKey = PrimaryKey("id")
    idx: Index = Index("name")


class Product(Table):
    id: Column = Column(Define.BIGINT(unsigned=True, auto_increment=True))
    product_name: Column = Column(Define.VARCHAR(255))
    product_price: Column = Column(Define.DECIMAL(12, 2))
    pk: PrimaryKey = PrimaryKey("id")
    idx: Index = Index("product_name")

# Define Database
class MyDatabase(Database):
    user: User = User()
    product: Product = Product()

# Instanciate Database
pool = Pool(host="localhost", user="root", password="Password_123456")
db = MyDatabase("db", pool)

# Synchronize Demo
def sync_demo(db: MyDatabase) -> None:
    db.Initialize()  # Initialize 'db'
    db.ShowDatabases()
    db.user.ShowCreateTable()
    db.user.ShowMetadata()
    db.user.Insert().Columns(db.user.name).Values(1).Execute(
        ["John", "Sarah"], many=True
    )
    db.Select("*").From(db.user).Execute()  # ((1, 'John'), (2, 'Sarah'))
    db.Drop()  # Drop 'db'

sync_demo(db)

# Asynchronize Demo
async def async_demo(db: MyDatabase) -> None:
    await db.aioInitialize()  # Initialize 'db'
    await db.aioShowDatabases()
    await db.user.aioShowCreateTable()
    await db.user.aioShowMetadata()
    await db.user.Insert().Columns(db.user.name).Values(1).aioExecute(
        ["John", "Sarah"], many=True
    )
    await db.Select("*").From(db.user).aioExecute()  # ((1, 'John'), (2, 'Sarah'))
    await db.aioDrop()  # Drop 'db'

asyncio.run(async_demo(db))
```

## Example (Temporary Table)

```python
import asyncio
from mysqlengine import Pool, Database, Table, TempTable
from mysqlengine import Column, Index, Define, PrimaryKey


class MyTable(Table):
    id: Column = Column(Define.BIGINT(unsigned=True, auto_increment=True))
    name: Column = Column(Define.VARCHAR(255))
    pk: PrimaryKey = PrimaryKey("id")


class MyTempTable(TempTable):
    id: Column = Column(Define.BIGINT(unsigned=True, auto_increment=True))
    name: Column = Column(Define.VARCHAR(255))
    pk: PrimaryKey = PrimaryKey("id")


class MyDatabase(Database):
    tb: MyTable = MyTable()


pool = Pool(host="localhost", user="root", password="Password_123456")
db = MyDatabase("db", pool)
db.Drop(True)

# Synchronize Demo
def sync_demo(db: MyDatabase) -> None:
    db.Initialize()  # Initialize 'db'
    db.tb.Insert().Columns("name").Values(1).Execute(["John", "Sarah"], many=True)
    with db.transaction() as conn:
        with db.CreateTempTable(conn, "temp_tb", MyTempTable()) as tmp:
            tmp.Insert().Columns("name").Select("name").From(db.tb).Execute()
            tmp.Select("*").Execute()  # ((1, 'John'), (2, 'Sarah'))
    # temporary table is automatically dropped
    db.Drop()  # Drop 'db'

sync_demo(db)

# Asynchronize Demo
async def async_demo(db: MyDatabase) -> None:
    await db.aioInitialize()  # Initialize 'db'
    await db.tb.Insert().Columns("name").Values(1).aioExecute(
        ["John", "Sarah"], many=True
    )
    async with db.transaction() as conn:
        async with db.CreateTempTable(conn, "temp_tb", MyTempTable()) as tmp:
            await tmp.Insert().Columns("name").Select("name").From(db.tb).aioExecute()
            await tmp.Select("*").aioExecute()  # ((1, 'John'), (2, 'Sarah'))
    # temporary table is automatically dropped
    await db.aioDrop()  # Drop 'db'

asyncio.run(async_demo(db))
```

## Example (Time Table)

```python
import asyncio
from mysqlengine import Pool, Database, TimeTable
from mysqlengine import Column, Index, Define, PrimaryKey


class MyTimeTable(TimeTable):
    id: Column = Column(Define.BIGINT(unsigned=True, auto_increment=True))
    name: Column = Column(Define.VARCHAR(255))
    dt: Column = Column(Define.DATETIME())
    pk: PrimaryKey = PrimaryKey("id", "dt")


class MyDatabase(Database):
    tb: MyTimeTable = MyTimeTable("dt", "YEAR", "2024-01-01", "2025-01-01")


pool = Pool(host="localhost", user="root", password="Password_123456")
db = MyDatabase("db", pool)
db.Drop(True)

# Synchronize Demo
def sync_demo(db: MyDatabase) -> None:
    db.Initialize()  # Initialize 'db'
    db.tb.Insert().Columns("name", "dt").Values(2).Execute(
        [("John", "2024-02-01"), ("Sarah", "2025-02-01")], many=True
    )
    db.tb.ShowPartitionRows()  # {'past': 0, 'y2024': 1, 'y2025': 1, 'future': 0}
    db.tb.ExtendToTime(end_with="2026-02-01")
    db.tb.ShowPartitionRows()  # {'past': 0, 'y2024': 1, 'y2025': 1, 'y2026': 0, 'future': 0}
    db.tb.DropToTime(start_from="2025-01-01")
    db.tb.ShowPartitionRows()  # {'past': 0, 'y2025': 1, 'y2026': 0, 'future': 0}
    db.Drop()  # Drop 'db'

sync_demo(db)

# Asynchronize Demo
async def async_demo(db: MyDatabase) -> None:
    await db.aioInitialize()  # Initialize 'db'
    await db.tb.Insert().Columns("name", "dt").Values(2).aioExecute(
        [("John", "2024-02-01"), ("Sarah", "2025-02-01")], many=True
    )
    await db.tb.aioShowPartitionRows()  # {'past': 0, 'y2024': 1, 'y2025': 1, 'future': 0}
    await db.tb.aioExtendToTime(end_with="2026-02-01")
    await db.tb.aioShowPartitionRows()  # {'past': 0, 'y2024': 1, 'y2025': 1, 'y2026': 0, 'future': 0}
    await db.tb.aioDropToTime(start_from="2025-01-01")
    await db.tb.aioShowPartitionRows()  # {'past': 0, 'y2025': 1, 'y2026': 0, 'future': 0}
    await db.aioDrop()  # Drop 'db'

asyncio.run(async_demo(db))
```

### Acknowledgements

MysqlEngine is based on several open-source repositories.

- [cytimes](https://github.com/AresJef/cyTimes)
- [numpy](https://github.com/numpy/numpy)
- [pandas](https://github.com/pandas-dev/pandas)
- [SQLCyCli](https://github.com/AresJef/SQLCyCli)
