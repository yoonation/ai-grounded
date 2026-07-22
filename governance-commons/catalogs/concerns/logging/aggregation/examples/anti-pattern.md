<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.aggregation aggregation and search readiness

## Anti-pattern A: Host-local logs only

```yaml
# docker-compose.yml
services:
  app:
    image: myapp:latest
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "5"
    # ← no log shipping; logs live and die on the host
```

Why this violates logging.aggregation: logs are written to the
host's local disk only. When the container or host is
restarted, the logs are lost. Cross-service incident
response is impossible because nothing is centralized.

## Anti-pattern B: SSH to host for log access

```markdown
# Incident response runbook

When a customer reports an issue:
1. Identify the host running their service (check K8s pod list)
2. ssh into the host
3. `kubectl logs <pod>` or `docker logs <container>`
4. grep for the error message
5. Cross-reference timestamps with other services manually
```

Why this violates logging.aggregation: ssh-to-host workflow is the
absence of aggregation. Cross-service correlation is manual;
historical analysis past the local rotation window is
impossible.

## Anti-pattern C: Aggregator without search capability

```python
# Logs are shipped to S3 as gzipped JSON files
# Query workflow:
def find_user_login(user_id, date_range):
    """Download N gigabytes of compressed logs and grep."""
    for date in date_range:
        for hour in range(24):
            obj = s3.get_object(
                Bucket='logs',
                Key=f'app/{date}/{hour}.json.gz'
            )
            for line in gzip.decompress(obj['Body'].read()).splitlines():
                if f'"user_id":"{user_id}"' in line:
                    yield json.loads(line)
```

Why this violates logging.aggregation: S3 alone is retention without
search. Each incident-response query downloads gigabytes and
greps. Sub-second response is impossible; incidents stretch
into hours waiting for grep.

## Anti-pattern D: Hour-scale shipping latency

```yaml
# fluent-bit configuration
[OUTPUT]
    Name              s3
    Match             *
    bucket            log-archive
    total_file_size   500M
    upload_timeout    1h  # ← logs batched for an hour before shipping
```

Why this violates logging.aggregation: a one-hour batch interval
means logs arrive at the aggregator up to an hour late.
During an active incident, the records the responder needs
are still in the local buffer; the aggregator shows the
state from an hour ago.

## Anti-pattern E: Inconsistent correlation field names

```python
# Service A
log.info("event", request_id=req_id, ...)

# Service B
log.info("event", req_id=request_id, ...)

# Service C
log.info("event", correlation_id=req_id, ...)

# Service D
log.info("event", trace=trace_id, ...)
```

Why this violates logging.aggregation: each service uses a different
field name for the same correlation. Cross-service queries
require knowing all four names and unioning. The substrate-
recommended posture is a documented field name (e.g.,
trace_id following W3C Trace Context).

## Anti-pattern F: Application admin has aggregator delete access

```yaml
AppAdminRole:
  policies:
    - resource: 'arn:aws:logs:*:*:*'
      actions: ['logs:*']  # ← includes logs:DeleteLogGroup
```

Why this violates logging.aggregation: application admins can delete
aggregator log groups. A compromised application admin
account can erase the audit trail. The substrate-recommended
separation places aggregator administration in a distinct
role.

## Anti-pattern G: No monitoring on shipping pipeline

```yaml
# fluent-bit running on every node;
# no metrics collected from fluent-bit;
# no alerts on fluent-bit failure.
```

Why this violates logging.aggregation: when a fluent-bit instance
fails, no alert fires. The first sign of trouble is during
incident response, when the responder notices logs are
missing for a host. The substrate-recommended remedy is
operational monitoring of the shipping pipeline itself.

## Cross-reference

- Good patterns: examples/logging/aggregation-good.md
- Substrate rule: logging.aggregation
