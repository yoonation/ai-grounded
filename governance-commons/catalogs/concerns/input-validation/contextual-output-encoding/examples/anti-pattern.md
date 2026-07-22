<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.contextual-output-encoding contextual output encoding (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: dangerouslySetInnerHTML with user input (React)

```jsx
// FORBIDDEN: user-supplied bio rendered as raw HTML.
// Attacker submits <script>fetch('/api/me').then(...)</script>
// in their profile bio.
function UserProfileBAD({ user }) {
  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <div dangerouslySetInnerHTML={{ __html: user.bio }} />
    </div>
  );
}
```

Why this violates input-validation.contextual-output-encoding:
- dangerouslySetInnerHTML injects the string as parsed HTML
- No sanitizer step interposed between user.bio and render
- Script tags in user.bio execute in the application origin

## Anti-pattern B: Jinja2 |safe filter on user input

```jinja2
{# FORBIDDEN: |safe disables auto-escape for user.bio.
   Any HTML/JS in user.bio renders unescaped. #}
<div>
  <h1>Welcome, {{ user.name }}</h1>
  <p>Bio: {{ user.bio | safe }}</p>
</div>
```

## Anti-pattern C: Django mark_safe on user input

```python
from django.utils.safestring import mark_safe

# FORBIDDEN: mark_safe wraps the string as SafeString, which
# Django then renders without escaping.
def render_bio_BAD(user_bio: str):
    return mark_safe(f"<p>{user_bio}</p>")
```

## Anti-pattern D: Vue v-html with user content

```vue
<template>
  <!-- FORBIDDEN: v-html renders the bound value as HTML. -->
  <div v-html="user.bio"></div>
</template>
```

## Anti-pattern E: Angular bypassSecurityTrust with user input

```typescript
import { DomSanitizer } from '@angular/platform-browser';

// FORBIDDEN: bypassSecurityTrustHtml accepts the string as
// trusted HTML, defeating Angular's default sanitization.
@Component({...})
export class UserBioComponent {
  trustedBio: SafeHtml;
  constructor(private sanitizer: DomSanitizer) {}
  ngOnInit() {
    this.trustedBio = this.sanitizer.bypassSecurityTrustHtml(this.user.bio);
  }
}
```

## Anti-pattern F: Handlebars triple-brace output

```handlebars
{{!-- FORBIDDEN: {{{ }}} disables HTML escaping. --}}
<div>{{{user.bio}}}</div>
```

## Anti-pattern G: Rails .html_safe on user input

```ruby
# FORBIDDEN: .html_safe marks the string as already-escaped,
# bypassing Rails's default ERB escaping. The user input is
# rendered verbatim.
def render_bio_BAD(user_bio)
  "<p>#{user_bio}</p>".html_safe
end
```

## Why mechanical detection fires on all of these

Semgrep registry rules detect:
- dangerouslySetInnerHTML invocations (with or without
  sanitizer adjacent; consumer-side rules can tighten this)
- v-html, bypassSecurityTrust* call sites
- |safe filter, mark_safe call sites
- {{{ }}} Handlebars output
- .html_safe and .raw helpers in Rails

All patterns map to CWE-79 / CWE-80 / CWE-116.
