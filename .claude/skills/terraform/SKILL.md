---
name: terraform
description: Terraform conventions and patterns. Use when writing, reviewing, or debugging Terraform code, HCL files, or infrastructure-as-code.
---

# Terraform Conventions

## Structure
- One resource per file when files exceed 200 lines
- Group related resources in the same file when small
- Variables in `variables.tf`, outputs in `outputs.tf`
- Use `terraform.tfvars` for environment-specific values, never commit it

## Naming
- Resources: snake_case, descriptive (`aws_iam_role.lambda_execution`)
- Variables: snake_case with clear purpose (`vpc_cidr_block`, not `cidr`)
- Outputs: snake_case matching the resource attribute they expose

## Patterns
- Prefer `for_each` over `count` — avoids index shift problems on removal
- Use `locals` for computed values and repeated expressions
- Use data sources to reference existing resources, never hardcode ARNs
- Remote state in S3 with DynamoDB lock table
- Use `sensitive = true` for any output containing secrets

## Security
- Never use `"*"` in IAM policy resources or actions unless explicitly justified
- Prefer IAM roles with OIDC over long-lived access keys
- Tag all resources: `environment`, `team`, `project`, `managed_by = "terraform"`
- Enable encryption at rest and in transit by default
- Use security groups with least-privilege ingress/egress rules

## Validation
- Run `terraform fmt` after every change
- Run `terraform validate` before plan
- Run `tflint` for linter checks
- Run `checkov` or `tfsec` for security scanning
- Always show `terraform plan` output before any apply

## Anti-Patterns
- Never use `terraform apply -auto-approve` in any environment
- Never hardcode AWS account IDs — use data sources or variables
- Never store state locally — always use remote backend
- Never use default VPC or default security groups
