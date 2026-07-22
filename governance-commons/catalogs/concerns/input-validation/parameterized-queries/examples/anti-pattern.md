<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.parameterized-queries parameterized queries (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: f-string SQL composition (Python)

```python
# FORBIDDEN: f-string interpolates email into the query.
# An attacker submits email="x' OR '1'='1" and bypasses the
# match.
def get_user_BAD(conn, email):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT id, name FROM users WHERE email = '{email}'"
        )
        return cur.fetchone()
```

Why this violates input-validation.parameterized-queries:
- The query string is constructed via f-string substitution
- Single-quote characters in the input close the literal and
  permit arbitrary SQL extension
- This is the canonical CWE-89 SQL injection pattern

## Anti-pattern B: + concatenation (Node.js)

```javascript
// FORBIDDEN: template literal concatenates email into the
// query. Same injection risk as Python f-strings.
async function getUserBAD(email) {
  const sql = "SELECT id, name FROM users WHERE email = '" + email + "'";
  const result = await pool.query(sql);
  return result.rows[0];
}
```

## Anti-pattern C: String.format SQL (Java)

```java
// FORBIDDEN: Statement (not PreparedStatement) plus String
// concatenation. An attacker controls the WHERE clause.
public User getUserBAD(Connection conn, String email) throws SQLException {
    String sql = "SELECT id, name FROM users WHERE email = '" + email + "'";
    try (Statement st = conn.createStatement();
         ResultSet rs = st.executeQuery(sql)) {
        if (rs.next()) {
            return new User(rs.getLong("id"), rs.getString("name"));
        }
        return null;
    }
}
```

## Anti-pattern D: Django .extra() with format string

```python
# FORBIDDEN: .extra() with a where clause that interpolates user
# input. Django ORM cannot parameterize the format-substituted
# string.
def search_users_BAD(query):
    return User.objects.extra(
        where=[f"name LIKE '%{query}%'"]
    )
```

## Anti-pattern E: Sequelize raw query with template literal

```javascript
// FORBIDDEN: raw query built with template literals.
async function findUsersBAD(emailDomain) {
  return await sequelize.query(
    `SELECT * FROM users WHERE email LIKE '%@${emailDomain}'`,
    { type: sequelize.QueryTypes.SELECT }
  );
}
```

## Anti-pattern F: Rails .find_by_sql with string interpolation

```ruby
# FORBIDDEN: .find_by_sql with interpolated user input.
class UserSearch
  def find_BAD(query)
    User.find_by_sql("SELECT * FROM users WHERE name LIKE '%#{query}%'")
  end
end
```

## Anti-pattern G: Go fmt.Sprintf

```go
// FORBIDDEN: Sprintf-built query.
func GetUserBAD(db *sql.DB, email string) (*User, error) {
    sql := fmt.Sprintf("SELECT id, name FROM users WHERE email = '%s'", email)
    var u User
    err := db.QueryRow(sql).Scan(&u.ID, &u.Name)
    return &u, err
}
```

## Why mechanical detection fires on all of these

Semgrep registry rules detect:
- String-builder patterns (f-strings, template literals,
  concatenation, sprintf) producing SQL
- Driver entry points (cursor.execute, query, executeQuery,
  QueryRow, find_by_sql) receiving the string-built query
- Combinations of the above where user input flows into the
  string

Each pattern matches a known CWE-89 signature.
