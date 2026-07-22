<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.resource-finalization resource not finalized

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Python open without with

```python
def read_config(path):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    return data
```

If `json.load(f)` raises (malformed JSON, IOError mid-read),
`f.close()` is never called. Under sustained errors the file
descriptor pool exhausts and the application begins failing
to open new files. The substrate's L1 binding flags `open()`
outside a `with` statement.

## Antipattern B: Python cursor without context

```python
def process_records(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM records")
    for row in cur:
        process(row)
    cur.close()
```

`cur.close()` runs only on normal completion. An exception
during processing leaves the cursor open; the connection
pool's per-connection cursor limit is reached over time.

## Antipattern C: Java try/finally with manual close

```java
Connection conn = null;
PreparedStatement ps = null;
ResultSet rs = null;
try {
    conn = ds.getConnection();
    ps = conn.prepareStatement(sql);
    ps.setString(1, id);
    rs = ps.executeQuery();
    return mapOrder(rs);
} finally {
    if (rs != null) try { rs.close(); } catch (Exception e) {}
    if (ps != null) try { ps.close(); } catch (Exception e) {}
    if (conn != null) try { conn.close(); } catch (Exception e) {}
}
```

The pattern works but is fragile: nested try/catch swallows
cleanup exceptions, the null checks proliferate per resource,
and developers commonly omit cleanup for one resource when
adding another. Try-with-resources eliminates all of this.

## Antipattern D: Go without defer

```go
func LoadOrder(ctx context.Context, db *sql.DB, id string) (*Order, error) {
    rows, err := db.QueryContext(ctx, "SELECT * FROM orders WHERE id = $1", id)
    if err != nil {
        return nil, err
    }
    if !rows.Next() {
        return nil, OrderNotFound{ID: id}
    }
    order, err := mapOrder(rows)
    if err != nil {
        return nil, err
    }
    rows.Close()
    return order, nil
}
```

`rows.Close()` runs only when `mapOrder` succeeds. On any
error path between `QueryContext` and the final return, rows
leaks. The Semgrep registry rule
`go.lang.best-practice.missing-defer-close` flags acquisition
without `defer Close`.

## Antipattern E: JavaScript stream without finalization

```javascript
async function processFile(path) {
  const stream = fs.createReadStream(path);
  for await (const chunk of stream) {
    process(chunk);
  }
}
```

If the for-await loop throws or returns early (e.g., from an
inner `process` failure), the stream is not destroyed. Node.js
emits a "no destroy() called" warning but does not auto-close.
The substrate-preferred pattern is `pipeline()` or explicit
try/finally with `stream.destroy()` in finally.

## Antipattern F: C# IDisposable without using

```csharp
public Order LoadOrder(string id)
{
    var conn = new NpgsqlConnection(connectionString);
    conn.Open();
    var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("id", id);
    var reader = cmd.ExecuteReader();
    if (reader.Read())
    {
        return MapOrder(reader);
    }
    return null;
}
```

Three IDisposable resources (NpgsqlConnection, NpgsqlCommand,
NpgsqlDataReader) and zero Dispose calls. The garbage
collector eventually finalizes them, but the connection pool
is exhausted long before. Roslyn analyzer CA2000 flags this.

## Antipattern G: Ruby File.open without block

```ruby
def read_config(path)
  f = File.open(path, 'r')
  config = JSON.parse(f.read)
  f.close
  config
end
```

Same pattern as Python: any error between `open` and `close`
leaks the file descriptor. The Ruby idiomatic alternative is
the block form: `File.open(path, 'r') { |f| ... }`.

## Antipattern H: Lock without ensure

```ruby
def critical_section
  @mutex.lock
  do_work
  @mutex.unlock
end
```

If `do_work` raises, `@mutex.unlock` is never called. The
mutex is permanently held; every other thread blocks forever.
The substrate-preferred pattern is `@mutex.synchronize { ... }`
which guarantees unlock.

## Antipattern I: Subprocess without close

```python
def run_command(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    return output
```

The subprocess's stdout pipe and the subprocess handle itself
are not finalized; the child process becomes a zombie if the
parent does not call `proc.wait()`. The substrate-preferred
pattern is `subprocess.run(...)` (which handles cleanup) or
`with subprocess.Popen(...) as proc:` (Python 3.2+).

## Remediation

For each antipattern above:

1. Wrap resource acquisition in the language's finalization
   construct: `with` (Python), `try-with-resources` (Java),
   `defer` (Go), `using` (C#), block form (Ruby), `use`
   (Kotlin).

2. For resources whose type does not implement the
   finalization protocol, add the implementation (define
   `__enter__`/`__exit__` in Python, implement `AutoCloseable`
   in Java, `IDisposable` in C#) rather than working around
   it in caller code.

3. For multi-resource acquisition with cleanup-order
   requirements beyond LIFO, use an explicit context manager
   (Python ExitStack, custom @contextmanager) that codifies
   the order.

4. Audit existing legacy code for the pattern; the substrate's
   L1 binding identifies opportunities for incremental
   refactor.
