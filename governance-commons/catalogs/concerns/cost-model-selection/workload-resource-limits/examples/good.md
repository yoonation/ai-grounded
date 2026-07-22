<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.workload-resource-limits workload resource limits (good patterns)

Substrate-original good-pattern examples for cost-model-selection.workload-resource-limits. These
illustrate the substrate-recommended pattern of declaring CPU
and memory limits on every workload across multiple orchestrator
platforms.

## Kubernetes: Deployment with explicit CPU and memory limits

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
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 512Mi
        - name: log-shipper
          image: fluent-bit:3.0.0
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 100m
              memory: 128Mi
```

Why this is good: both containers (app and sidecar) declare both
resources.requests and resources.limits. The substrate-required
L1 floor (limits present) is satisfied. The substrate-recommended
addition (requests aligned with limits per the consumer's QoS
policy) is also satisfied: the Burstable QoS class results from
requests less than limits. kube-linter's required-resource-limit
check passes.

The substrate-recommended namespace-level second line of defense
is also in place:

```yaml
# LimitRange in the same namespace
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
    - type: Container
      default:
        cpu: 500m
        memory: 256Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      min:
        cpu: 50m
        memory: 64Mi
      max:
        cpu: 4000m
        memory: 8Gi
```

The LimitRange defaults catch any pod that slips past PR-level
linting; the min/max bounds prevent extreme outliers.

## AWS Lambda: explicit MemorySize and Timeout

```hcl
resource "aws_lambda_function" "payments_processor" {
  function_name = "payments-processor-${var.environment}"
  runtime       = "python3.12"
  handler       = "lambda_function.handler"
  filename      = data.archive_file.lambda.output_path

  memory_size = 512
  timeout     = 30

  tags = merge(local.common_tags, {
    role = "event-processor"
  })
}
```

Why this is good: memory_size is declared explicitly (the cost-
relevant Lambda configuration; Lambda CPU is proportional to
memory). timeout is declared explicitly (paired with memory_size
as the substrate-recommended bounded-cost configuration). tflint
with the substrate's cost.lambda-default-memory rule passes.

## Cloud Run: resources.limits on the service revision

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: payments-processor
spec:
  template:
    spec:
      containers:
        - image: gcr.io/my-project/payments-processor:1.42.0
          resources:
            limits:
              cpu: "2"
              memory: "1Gi"
          env:
            - name: ENVIRONMENT
              value: production
```

Why this is good: resources.limits.cpu and resources.limits.memory
are declared explicitly on the Cloud Run service revision. Cloud
Run's default behavior allocates a substrate-recommended-against
default if these are omitted; the explicit declaration is the
substrate-recommended pattern.

The Terraform equivalent:

```hcl
resource "google_cloud_run_v2_service" "payments_processor" {
  name     = "payments-processor"
  location = "us-central1"

  template {
    containers {
      image = "gcr.io/my-project/payments-processor:1.42.0"
      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }
  }
}
```

## AWS ECS Fargate: task-level and container-level resources

```hcl
resource "aws_ecs_task_definition" "payments_processor" {
  family                   = "payments-processor"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  # Task-level (Fargate-required)
  cpu    = "1024"
  memory = "2048"

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "${var.account}.dkr.ecr.${var.region}.amazonaws.com/payments-processor:1.42.0"
      essential = true
      cpu       = 768   # container-level under task ceiling
      memory    = 1536
      memoryReservation = 1024
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/payments-processor"
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    },
    {
      name      = "log-shipper"
      image     = "amazon/aws-for-fluent-bit:stable"
      essential = false
      cpu       = 128
      memory    = 256
    }
  ])

  tags = merge(local.common_tags, {
    role = "ecs-task"
  })
}
```

Why this is good: task-level cpu and memory are declared at the
Fargate-required level. Container-level cpu, memory, and
memoryReservation are declared per container; the container
allocations sum within the task ceiling. Both sidecar and primary
container declare their resource share. cfn-lint's CKV_AWS_173
equivalent passes.

## Azure Container Apps: resources block on the container

```hcl
resource "azurerm_container_app" "payments_processor" {
  name                         = "payments-processor"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "app"
      image  = "${var.acr_login_server}/payments-processor:1.42.0"
      cpu    = 1.0
      memory = "2Gi"

      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
    }
  }

  tags = merge(local.common_tags, {
    role = "container-app"
  })
}
```

Why this is good: cpu and memory are declared at the container
level (Azure Container Apps requires both). The substrate's L1
rule's mechanical core (resource limits present) is satisfied.

## What the orchestrator admission policy catches

Even with PR-level linting in place, the substrate-recommended
admission policy catches the case where a developer creates a
workload outside the CI pipeline (kubectl apply directly; a
hotfix script that bypasses review). The Kyverno policy:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-pod-resources
spec:
  validationFailureAction: Enforce
  rules:
    - name: validate-resources
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: >
          Every container must declare resources.limits.cpu and
          resources.limits.memory per cost-model-selection.workload-resource-limits.
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    cpu: "?*"
                    memory: "?*"
```

When a pod is created without limits, Kyverno rejects it at the
API server. The cost-model-selection.workload-resource-limits rule's intent is realized end-to-end
from IaC source through to runtime admission.

## Why the limit values are right-sized

The good examples above set limits that reflect a substrate-
recommended sizing analysis: the substrate-recommended pattern is
"set the limit to 1.5x the observed p99 usage over a representative
production window." For new workloads without production data,
conservative initial limits are set and revisited after the
workload's initial soak period.

The right-sizing question is L2 review scope (cost-model-selection.cost-emission-pipeline
pipeline review); the L1 rule's concern is only that limits
exist. The good examples show limits that pass L1 mechanically
and also reflect L2-appropriate right-sizing.
