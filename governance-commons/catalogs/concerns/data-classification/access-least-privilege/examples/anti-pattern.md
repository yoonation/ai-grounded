<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.access-least-privilege access least privilege (anti-pattern)

Substrate-original illustration.

```hcl
# A shared service role with blanket read on a restricted table, no audit.
resource "aws_iam_policy" "app_blanket" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:*"]          # all actions
      Resource = "*"                      # all tables, including restricted
    }]
  })
  # attached to the shared application role every service assumes
}
# no CloudTrail data-event logging on the restricted table
```

## Why this violates the rule

Every service that assumes the shared application role can read the restricted
table, so the need-to-know set is effectively everyone, and there is no
data-event audit trail to detect or investigate misuse. A single compromised
or misused credential reaches the restricted data, and the access leaves no
record. Minimizing the grant to a justified role and enabling access logging
is the fix.
