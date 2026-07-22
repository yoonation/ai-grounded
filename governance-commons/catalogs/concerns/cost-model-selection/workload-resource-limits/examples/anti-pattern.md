<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.workload-resource-limits workload resource limits (anti-patterns)

Substrate-original anti-pattern examples for cost-model-selection.workload-resource-limits. Each
shows a common way the rule is violated and explains why the
violation matters.

## Anti-pattern 1: Pod with no resources block at all

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
    spec:
      containers:
        - name: app
          image: payments-api:1.42.0
          # no resources block at all
```

Why this fails: the container has no CPU or memory limit. The
pod runs as BestEffort QoS class (lowest priority for the
scheduler; first to evict under node pressure). The cost ceiling
is unbounded: a memory leak consumes node memory until the
kernel OOM killer terminates the workload, but before that
point it may have evicted other workloads on the same node.

kube-linter's required-resource-limit check fails. Kyverno or
Gatekeeper rejects at admission time if the substrate-recommended
admission policy is deployed. The substrate's Semgrep registry
rule catches this in PR review.

## Anti-pattern 2: Requests declared but limits omitted

```yaml
spec:
  containers:
    - name: app
      image: payments-api:1.42.0
      resources:
        requests:
          cpu: 250m
          memory: 256Mi
        # no limits block
```

Why this fails: requests reserve capacity at scheduling time
but do not bound runtime consumption. A pod with requests of
250m CPU but no CPU limit can consume the entire node's CPU
if available; the cost consequence is the same as no resources
block at all in the absence of node pressure.

This anti-pattern is more insidious than complete absence because
reviewers may approve the PR thinking "resources are declared."
The substrate's discipline is that the L1 rule's mechanical core
requires resources.limits.cpu and resources.limits.memory; only
requests is a finding.

The substrate's Semgrep rule yaml.kubernetes.security.kubernetes-
container-only-requests catches this specifically.

## Anti-pattern 3: Sidecar missing limits while primary container has them

```yaml
spec:
  containers:
    - name: app
      image: payments-api:1.42.0
      resources:
        requests:
          cpu: 250m
          memory: 256Mi
        limits:
          cpu: 1000m
          memory: 512Mi
    - name: log-shipper
      image: fluent-bit:3.0.0
      # no resources block on the sidecar
```

Why this fails: the primary container is bounded but the sidecar
is unbounded. Sidecars often consume more resources than expected
under load (log volume spikes during incidents; metric scraping
overhead grows with cardinality); an unbounded sidecar can drive
the entire pod into eviction even when the primary container is
within its limits.

The substrate's L1 rule applies per-container, not per-pod. Every
container including init containers, ephemeral containers, and
sidecar containers requires the limit declaration. Reviewers
verify by listing every container in the pod spec and confirming
each has the limits block.

## Anti-pattern 4: Lambda using default MemorySize

```hcl
resource "aws_lambda_function" "payments_processor" {
  function_name = "payments-processor"
  runtime       = "python3.12"
  handler       = "lambda_function.handler"
  filename      = data.archive_file.lambda.output_path
  # memory_size not declared; defaults to 128 MB
}
```

Why this fails: AWS Lambda's default MemorySize is 128 MB, and
CPU allocation is proportional to memory. A function expecting
to handle non-trivial workloads at 128 MB hits memory pressure
and either OOMs (cost: failed invocations plus retry storm) or
runs slowly enough that invocation cost compounds (Lambda billing
is duration-times-memory). Neither is cost-bounded by the
consumer's design.

The substrate's discipline is explicit memory_size declaration so
the cost ceiling is consumer-controlled rather than provider-
default. terraform.aws.cost.lambda-default-memory in the
substrate's Semgrep rules catches this.

## Anti-pattern 5: ECS task without container-level resources

```hcl
resource "aws_ecs_task_definition" "payments_processor" {
  family                   = "payments-processor"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "1024"
  memory = "2048"

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "...payments-processor:1.42.0"
      essential = true
      # no cpu or memory at the container level
    },
    {
      name      = "log-shipper"
      image     = "amazon/aws-for-fluent-bit:stable"
      essential = false
      # no cpu or memory at the container level
    }
  ])
}
```

Why this fails: task-level cpu and memory are declared (Fargate
requires this) but container-level cpu and memory are omitted.
Fargate treats container-level omission as "share the task
ceiling," which can produce a runaway container that consumes
the entire task budget and starves its sidecar. The substrate's
recommended pattern is explicit container-level allocations
summing to the task ceiling.

The substrate's Semgrep rule yaml.cloudformation.cost.ecs-task-no-
resources catches this.

## Anti-pattern 6: Cloud Run service relying on default resources

```hcl
resource "google_cloud_run_v2_service" "payments_processor" {
  name     = "payments-processor"
  location = "us-central1"

  template {
    containers {
      image = "gcr.io/my-project/payments-processor:1.42.0"
      # no resources block
    }
  }
}
```

Why this fails: Cloud Run's default resources are not the
substrate-recommended sizing. The default is sufficient for many
workloads but is not consumer-controlled; if the substrate's
cost model commits to a specific resource ceiling per workload,
the absent declaration leaves the ceiling provider-default.

The substrate's discipline is explicit consumer-side declaration
even where the provider default would work. terraform.gcp.cost.
cloudrun-no-limits catches this.

## Anti-pattern 7: Helm chart that templates limits via complex inheritance

```yaml
# values.yaml
resources: {}

# templates/deployment.yaml
spec:
  containers:
    - name: app
      image: payments-api:1.42.0
      resources: {{ toYaml .Values.resources | nindent 12 }}
```

Why this fails: the chart compiles to a Deployment with an empty
resources block when the consumer does not override
.Values.resources. The chart source-level linting may pass (the
template carries a resources reference) but the rendered manifest
fails. The kube-linter run against rendered chart output catches
this; the substrate's recommended CI pattern is to render the
chart and lint the rendered output, not the template source
alone.

The substrate-recommended chart pattern is to set defaults in
values.yaml that the consumer can override but that work as a
substrate-required floor:

```yaml
# values.yaml (substrate-recommended chart default)
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

## Anti-pattern 8: Right-sized values but wrong direction

```yaml
spec:
  containers:
    - name: app
      image: payments-api:1.42.0
      resources:
        requests:
          cpu: 4000m
          memory: 8Gi
        limits:
          cpu: 100m
          memory: 128Mi
```

Why this fails: requests exceed limits. Kubernetes rejects this
at admission time. The configuration is internally inconsistent;
the developer likely swapped the values. The substrate's
mechanical L1 check (limits present) passes, but the workload
will not run.

This anti-pattern is caught by Kubernetes itself rather than by
the substrate's binding, but the substrate's review-checklist
discipline catches it earlier: reviewers verify limits are
greater than or equal to requests as part of the resource-block
review.

## What the consequences look like in operation

A team with consistent cost-model-selection.workload-resource-limits violations sees the
consequences when a workload misbehaves:

- A memory leak in one workload evicts unrelated workloads on
  the same node, triggering a cascade incident the team
  responds to in production without understanding the cost
  consequence (cascade restart costs; downstream retry storms)
- A misconfigured runaway loop consumes a node CPU until manual
  intervention; the cost-anomaly alert (cost-model-selection.cost-anomaly-alerting) fires
  account-wide because per-workload attribution is degraded by
  the noisy neighbor
- The cost-model ADR (cost-model-selection.cost-model-selection-policy) commits to a per-workload
  cost ceiling that the L1 rule does not enforce; the team is
  surprised when month-end invoice exceeds the documented
  ceiling

The substrate's discipline is to enforce L1 at PR time, at
admission time, and via namespace-level LimitRange, so the
runtime cost ceiling is consumer-controlled at every layer.
