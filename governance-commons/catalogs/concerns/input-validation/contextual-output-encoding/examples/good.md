<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.contextual-output-encoding contextual output encoding

Substrate-original good patterns. Adapt to your stack.

## Pattern A: React text children (automatic escape)

```jsx
function UserProfile({ user }) {
  // Text children are auto-escaped by React. Special characters
  // in user.name appear as text, not as HTML.
  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <p>Bio: {user.bio}</p>
    </div>
  );
}
```

## Pattern B: Jinja2 with autoescape (default for Flask)

```jinja2
{# autoescape is on by default for Flask's render_template;
   user.name appears as escaped HTML text. #}
<div>
  <h1>Welcome, {{ user.name }}</h1>
  <p>Bio: {{ user.bio }}</p>
</div>
```

## Pattern C: Vue text binding

```vue
<template>
  <!-- {{ }} text interpolation is auto-escaped. -->
  <div>
    <h1>Welcome, {{ user.name }}</h1>
    <p>Bio: {{ user.bio }}</p>
  </div>
</template>
```

## Pattern D: Sanitized HTML output via DOMPurify (React)

```jsx
import DOMPurify from 'dompurify';

const ALLOWED_HTML_CONFIG = {
  ALLOWED_TAGS: ['p', 'strong', 'em', 'ul', 'ol', 'li', 'a'],
  ALLOWED_ATTR: ['href'],
};

function RichTextDisplay({ userMarkup }) {
  // Intentionally raw HTML output: blog post content the user
  // authored. DOMPurify enforces an allowlist before render.
  const safeHtml = DOMPurify.sanitize(userMarkup, ALLOWED_HTML_CONFIG);
  return <div dangerouslySetInnerHTML={{ __html: safeHtml }} />;
}
```

dangerouslySetInnerHTML is used intentionally, with DOMPurify
applied immediately before. The allowlist policy is explicit
and reviewable.

## Pattern E: Sanitized HTML in Python with bleach (Flask + Jinja2)

```python
import bleach
from markupsafe import Markup

ALLOWED_TAGS = ["p", "strong", "em", "ul", "ol", "li", "a"]
ALLOWED_ATTRS = {"a": ["href", "title"]}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

@app.template_filter("sanitize_html")
def sanitize_html_filter(value: str) -> Markup:
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return Markup(cleaned)
```

```jinja2
{# Sanitized rich-text content from a Markdown editor.
   The filter applies bleach with the allowlist before
   Markup wraps the result for raw rendering. #}
<div class="user-content">{{ user.bio | sanitize_html }}</div>
```

## Pattern F: Angular property binding (automatic sanitization)

```typescript
// Angular's property binding sanitizes by default.
// userBio appears as text in the DOM, not as parsed HTML.
@Component({
  template: `<div>{{ user.bio }}</div>`
})
export class UserBioComponent {
  @Input() user!: User;
}
```
