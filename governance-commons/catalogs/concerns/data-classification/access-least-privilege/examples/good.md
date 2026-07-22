<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.access-least-privilege access least privilege (good pattern)

Substrate-original illustration.

```hcl
# Read access to restricted data is granted only to a minimized, justified
# role, and access is logged to an audit trail.
resource "aws_iam_policy" "health_reader" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:Query"]
      Resource = aws_dynamodb_table.health_records.arn
      # attached only to the clinical-service role, justified by purpose
    }]
  })
}

resource "aws_cloudtrail" "health_access" {
  # data-event logging on the restricted table: who read what, when
  event_selector {
    data_resource {
      type   = "AWS::DynamoDB::Table"
      values = [aws_dynamodb_table.health_records.arn]
    }
  }
}
```

## Why this satisfies the rule

Read access to the restricted table is granted to a single justified role
rather than a shared blanket grant, and data-event logging records every
access for audit. The principal set is minimized to need-to-know, and misuse
would be detectable in the trail.
