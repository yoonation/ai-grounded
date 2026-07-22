<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.resource-finalization resource finalization

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python with statement

```python
def read_config(path: Path) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

def process_records(connection):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM records")
        for row in cur:
            yield row
```

`with` ensures the file or cursor closes on normal exit and on
exception. The context manager protocol is the substrate-
preferred resource discipline.

## Pattern B: Python ExitStack for variable-count resources

```python
from contextlib import ExitStack

def process_batch(paths: list[Path]):
    with ExitStack() as stack:
        files = [stack.enter_context(open(p, 'r')) for p in paths]
        for f in files:
            for line in f:
                process_line(line)
```

ExitStack manages a dynamic number of resources; cleanup runs
in reverse acquisition order automatically.

## Pattern C: Java try-with-resources

```java
public Order loadOrder(DataSource ds, String id) throws SQLException {
    String sql = "SELECT * FROM orders WHERE id = ?";
    try (Connection conn = ds.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {
        ps.setString(1, id);
        try (ResultSet rs = ps.executeQuery()) {
            return rs.next() ? mapOrder(rs) : null;
        }
    }
}
```

Three resources (Connection, PreparedStatement, ResultSet) are
managed by nested try-with-resources. Cleanup runs in reverse
order; exceptions during cleanup are suppressed (the original
exception propagates).

## Pattern D: Go defer for cleanup

```go
func LoadOrder(ctx context.Context, db *sql.DB, id string) (*Order, error) {
    rows, err := db.QueryContext(ctx, "SELECT * FROM orders WHERE id = $1", id)
    if err != nil {
        return nil, fmt.Errorf("query: %w", err)
    }
    defer rows.Close()
    if rows.Next() {
        return mapOrder(rows)
    }
    return nil, OrderNotFound{ID: id}
}

func ProcessFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("open %s: %w", path, err)
    }
    defer f.Close()
    return process(f)
}
```

`defer` immediately after acquisition registers the cleanup;
it runs on every function exit path including panic.

## Pattern E: C# using declaration

```csharp
public Order LoadOrder(string id)
{
    using var conn = new NpgsqlConnection(connectionString);
    conn.Open();
    using var cmd = new NpgsqlCommand("SELECT * FROM orders WHERE id = @id", conn);
    cmd.Parameters.AddWithValue("id", id);
    using var reader = cmd.ExecuteReader();
    return reader.Read() ? MapOrder(reader) : null;
}
```

C# 8+ `using var` scopes cleanup to the enclosing block. The
runtime guarantees Dispose on exit.

## Pattern F: Ruby block-with-cleanup

```ruby
def read_config(path)
  File.open(path, 'r') do |f|
    JSON.parse(f.read)
  end
end

def process_records(connection)
  connection.transaction do
    Record.find_each do |record|
      process(record)
    end
  end
end
```

`File.open` with a block closes the file on block exit. The
transaction block commits on normal exit and rolls back on
exception.

## Pattern G: Kotlin use extension

```kotlin
fun loadOrder(ds: DataSource, id: String): Order? {
    return ds.connection.use { conn ->
        conn.prepareStatement("SELECT * FROM orders WHERE id = ?").use { ps ->
            ps.setString(1, id)
            ps.executeQuery().use { rs ->
                if (rs.next()) mapOrder(rs) else null
            }
        }
    }
}
```

`use` calls close on the Closeable when the lambda returns or
throws.

## Pattern H: Multi-resource ordered cleanup

```python
# When cleanup order matters beyond LIFO
from contextlib import contextmanager

@contextmanager
def acquire_with_ordered_cleanup(primary, secondary):
    try:
        secondary.acquire()
        try:
            primary.acquire()
            yield (primary, secondary)
        finally:
            primary.release()
    finally:
        secondary.release()
```

The substrate-acceptable pattern for cleanup ordering beyond
LIFO is an explicit context manager that codifies the order;
the consumer uses the manager with `with` so the LIFO
discipline is preserved at the call site.
