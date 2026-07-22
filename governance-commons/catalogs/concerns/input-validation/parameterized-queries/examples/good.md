<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.parameterized-queries parameterized queries

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python psycopg with parameter argument

```python
import psycopg

def get_user_by_email(conn, email: str):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, email FROM users WHERE email = %s",
            (email,),
        )
        return cur.fetchone()
```

The query template is a constant string; the user-supplied
`email` is passed as a parameter. The driver transmits the
template and parameter over separate channels.

## Pattern B: Python SQLAlchemy ORM

```python
from sqlalchemy.orm import Session
from app.models import User

def get_user_by_email(session: Session, email: str):
    return session.query(User).filter(User.email == email).first()
```

The ORM's expression builder parameterizes by construction. No
SQL string appears in application code.

## Pattern C: Node.js with pg driver

```javascript
const { Pool } = require('pg');
const pool = new Pool();

async function getUserByEmail(email) {
  const result = await pool.query(
    'SELECT id, name, email FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0];
}
```

The query uses $1 placeholder; the email is passed in the
values array.

## Pattern D: Java JDBC with PreparedStatement

```java
public Optional<User> getUserByEmail(Connection conn, String email)
    throws SQLException {
  String sql = "SELECT id, name, email FROM users WHERE email = ?";
  try (PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.setString(1, email);
    try (ResultSet rs = ps.executeQuery()) {
      if (rs.next()) {
        return Optional.of(new User(
          rs.getLong("id"),
          rs.getString("name"),
          rs.getString("email")
        ));
      }
      return Optional.empty();
    }
  }
}
```

PreparedStatement with `?` placeholder; setString binds the
parameter.

## Pattern E: Go database/sql

```go
func GetUserByEmail(ctx context.Context, db *sql.DB, email string) (*User, error) {
    var u User
    err := db.QueryRowContext(ctx,
        "SELECT id, name, email FROM users WHERE email = $1",
        email,
    ).Scan(&u.ID, &u.Name, &u.Email)
    if err != nil {
        return nil, err
    }
    return &u, nil
}
```

QueryRowContext takes the query template and variadic args; the
driver parameterizes.

## Pattern F: Allowlisted dynamic ORDER BY direction

```python
ALLOWED_ORDER = {"asc": "ASC", "desc": "DESC"}

def list_users(conn, order: str):
    direction = ALLOWED_ORDER.get(order.lower())
    if direction is None:
        raise ValueError("invalid order direction")
    with conn.cursor() as cur:
        # direction is from a closed set; safe to interpolate
        cur.execute(f"SELECT id, name FROM users ORDER BY name {direction}")
        return cur.fetchall()
```

ORDER BY direction cannot be a parameter (SQL grammar limitation),
so the substrate-recommended pattern allowlists the permitted
values before any string construction.
