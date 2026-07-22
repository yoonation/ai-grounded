# Review checklist manifest (L2)

These rules are enforced by human or AI review, not by a gate. Each links
to its checklist. Wire them into your pull-request template or review bot.

## agentic-systems
- agentic-systems.action-bounds  (governance-commons/catalogs/concerns/agentic-systems/action-bounds/checklist.md)
- agentic-systems.agent-action-audit-record  (governance-commons/catalogs/concerns/agentic-systems/agent-action-audit-record/checklist.md)
- agentic-systems.agent-memory-integrity  (governance-commons/catalogs/concerns/agentic-systems/agent-memory-integrity/checklist.md)
- agentic-systems.delegation-authority  (governance-commons/catalogs/concerns/agentic-systems/delegation-authority/checklist.md)
- agentic-systems.human-action-gating  (governance-commons/catalogs/concerns/agentic-systems/human-action-gating/checklist.md)
- agentic-systems.instruction-data-separation  (governance-commons/catalogs/concerns/agentic-systems/instruction-data-separation/checklist.md)
- agentic-systems.tool-authorization-scope  (governance-commons/catalogs/concerns/agentic-systems/tool-authorization-scope/checklist.md)
- agentic-systems.tool-use-authorization  (governance-commons/catalogs/concerns/agentic-systems/tool-use-authorization/checklist.md)

## authentication
- authentication.account-lockout  (governance-commons/catalogs/concerns/authentication/account-lockout/checklist.md)
- authentication.generic-failure-responses  (governance-commons/catalogs/concerns/authentication/generic-failure-responses/checklist.md)
- authentication.mfa-enrollment  (governance-commons/catalogs/concerns/authentication/mfa-enrollment/checklist.md)
- authentication.mfa-on-privileged-operations  (governance-commons/catalogs/concerns/authentication/mfa-on-privileged-operations/checklist.md)
- authentication.no-credentials-in-logs  (governance-commons/catalogs/concerns/authentication/no-credentials-in-logs/checklist.md)
- authentication.password-policy  (governance-commons/catalogs/concerns/authentication/password-policy/checklist.md)
- authentication.rate-limiting  (governance-commons/catalogs/concerns/authentication/rate-limiting/checklist.md)
- authentication.session-regeneration  (governance-commons/catalogs/concerns/authentication/session-regeneration/checklist.md)
- authentication.token-expiration  (governance-commons/catalogs/concerns/authentication/token-expiration/checklist.md)

## authorization
- authorization.audit-events-on-decisions  (governance-commons/catalogs/concerns/authorization/audit-events-on-decisions/checklist.md)
- authorization.authz-before-resource-access  (governance-commons/catalogs/concerns/authorization/authz-before-resource-access/checklist.md)
- authorization.centralized-deny-by-default-policy  (governance-commons/catalogs/concerns/authorization/centralized-deny-by-default-policy/checklist.md)
- authorization.least-privilege-role-design  (governance-commons/catalogs/concerns/authorization/least-privilege-role-design/checklist.md)
- authorization.multi-tenant-data-layer-isolation  (governance-commons/catalogs/concerns/authorization/multi-tenant-data-layer-isolation/checklist.md)
- authorization.no-client-side-only-authz  (governance-commons/catalogs/concerns/authorization/no-client-side-only-authz/checklist.md)
- authorization.object-level-authorization  (governance-commons/catalogs/concerns/authorization/object-level-authorization/checklist.md)
- authorization.protected-route-declares-authz  (governance-commons/catalogs/concerns/authorization/protected-route-declares-authz/checklist.md)
- authorization.step-up-and-audit-for-privilege-changes  (governance-commons/catalogs/concerns/authorization/step-up-and-audit-for-privilege-changes/checklist.md)

## backup-recovery
- backup-recovery.coverage-and-objectives  (governance-commons/catalogs/concerns/backup-recovery/coverage-and-objectives/checklist.md)
- backup-recovery.restore-verification  (governance-commons/catalogs/concerns/backup-recovery/restore-verification/checklist.md)

## code-organization
- code-organization.dependency-direction-layering  (governance-commons/catalogs/concerns/code-organization/dependency-direction-layering/checklist.md)
- code-organization.duplication-and-abstraction  (governance-commons/catalogs/concerns/code-organization/duplication-and-abstraction/checklist.md)
- code-organization.module-boundary-cohesion  (governance-commons/catalogs/concerns/code-organization/module-boundary-cohesion/checklist.md)
- code-organization.public-interface-minimalism  (governance-commons/catalogs/concerns/code-organization/public-interface-minimalism/checklist.md)

## configuration-management
- configuration-management.layering-and-parity  (governance-commons/catalogs/concerns/configuration-management/layering-and-parity/checklist.md)
- configuration-management.startup-validation  (governance-commons/catalogs/concerns/configuration-management/startup-validation/checklist.md)

## cost-model-selection
- cost-model-selection.cost-anomaly-alerting  (governance-commons/catalogs/concerns/cost-model-selection/cost-anomaly-alerting/checklist.md)
- cost-model-selection.cost-emission-pipeline  (governance-commons/catalogs/concerns/cost-model-selection/cost-emission-pipeline/checklist.md)

## data-classification
- data-classification.access-least-privilege  (governance-commons/catalogs/concerns/data-classification/access-least-privilege/checklist.md)
- data-classification.classification-correctness  (governance-commons/catalogs/concerns/data-classification/classification-correctness/checklist.md)
- data-classification.encryption-per-class  (governance-commons/catalogs/concerns/data-classification/encryption-per-class/checklist.md)
- data-classification.model-classification-label  (governance-commons/catalogs/concerns/data-classification/model-classification-label/checklist.md)
- data-classification.no-classified-data-in-logs  (governance-commons/catalogs/concerns/data-classification/no-classified-data-in-logs/checklist.md)
- data-classification.propagation-inheritance  (governance-commons/catalogs/concerns/data-classification/propagation-inheritance/checklist.md)
- data-classification.retention-disposal  (governance-commons/catalogs/concerns/data-classification/retention-disposal/checklist.md)

## dependency-management
- dependency-management.provenance  (governance-commons/catalogs/concerns/dependency-management/provenance/checklist.md)
- dependency-management.update-cadence  (governance-commons/catalogs/concerns/dependency-management/update-cadence/checklist.md)

## documentation
- documentation.accuracy-and-sync  (governance-commons/catalogs/concerns/documentation/accuracy-and-sync/checklist.md)
- documentation.decisions-and-operations  (governance-commons/catalogs/concerns/documentation/decisions-and-operations/checklist.md)

## error-handling
- error-handling.error-response-contract  (governance-commons/catalogs/concerns/error-handling/error-response-contract/checklist.md)
- error-handling.error-status-code  (governance-commons/catalogs/concerns/error-handling/error-status-code/checklist.md)
- error-handling.observable-response-discrepancy  (governance-commons/catalogs/concerns/error-handling/observable-response-discrepancy/checklist.md)
- error-handling.retry-and-circuit-breaker  (governance-commons/catalogs/concerns/error-handling/retry-and-circuit-breaker/checklist.md)
- error-handling.typed-error-classification  (governance-commons/catalogs/concerns/error-handling/typed-error-classification/checklist.md)

## feature-flags
- feature-flags.lifecycle-and-kill-switch  (governance-commons/catalogs/concerns/feature-flags/lifecycle-and-kill-switch/checklist.md)
- feature-flags.staged-rollout-and-context  (governance-commons/catalogs/concerns/feature-flags/staged-rollout-and-context/checklist.md)

## infrastructure-misconfiguration
- infrastructure-misconfiguration.deletion-protection-and-drift  (governance-commons/catalogs/concerns/infrastructure-misconfiguration/deletion-protection-and-drift/checklist.md)
- infrastructure-misconfiguration.governance-tagging  (governance-commons/catalogs/concerns/infrastructure-misconfiguration/governance-tagging/checklist.md)
- infrastructure-misconfiguration.key-management-design  (governance-commons/catalogs/concerns/infrastructure-misconfiguration/key-management-design/checklist.md)
- infrastructure-misconfiguration.least-privilege-iac-iam  (governance-commons/catalogs/concerns/infrastructure-misconfiguration/least-privilege-iac-iam/checklist.md)
- infrastructure-misconfiguration.network-segmentation  (governance-commons/catalogs/concerns/infrastructure-misconfiguration/network-segmentation/checklist.md)
- infrastructure-misconfiguration.state-backend-hardening  (governance-commons/catalogs/concerns/infrastructure-misconfiguration/state-backend-hardening/checklist.md)

## input-validation
- input-validation.canonical-encoding-before-validation  (governance-commons/catalogs/concerns/input-validation/canonical-encoding-before-validation/checklist.md)
- input-validation.deserialization-safe-loaders  (governance-commons/catalogs/concerns/input-validation/deserialization-safe-loaders/checklist.md)
- input-validation.file-upload-validation  (governance-commons/catalogs/concerns/input-validation/file-upload-validation/checklist.md)
- input-validation.schema-validation-at-boundary  (governance-commons/catalogs/concerns/input-validation/schema-validation-at-boundary/checklist.md)
- input-validation.ssrf-prevention  (governance-commons/catalogs/concerns/input-validation/ssrf-prevention/checklist.md)
- input-validation.type-narrowing-at-boundary  (governance-commons/catalogs/concerns/input-validation/type-narrowing-at-boundary/checklist.md)

## logging
- logging.aggregation  (governance-commons/catalogs/concerns/logging/aggregation/checklist.md)
- logging.correlation-ids  (governance-commons/catalogs/concerns/logging/correlation-ids/checklist.md)
- logging.integrity  (governance-commons/catalogs/concerns/logging/integrity/checklist.md)
- logging.no-sensitive-data-in-logs  (governance-commons/catalogs/concerns/logging/no-sensitive-data-in-logs/checklist.md)
- logging.redaction  (governance-commons/catalogs/concerns/logging/redaction/checklist.md)
- logging.retention-policy  (governance-commons/catalogs/concerns/logging/retention-policy/checklist.md)

## monitoring-alerting
- monitoring-alerting.alert-lifecycle  (governance-commons/catalogs/concerns/monitoring-alerting/alert-lifecycle/checklist.md)
- monitoring-alerting.detection-coverage  (governance-commons/catalogs/concerns/monitoring-alerting/detection-coverage/checklist.md)
- monitoring-alerting.on-call-rotation-coverage  (governance-commons/catalogs/concerns/monitoring-alerting/on-call-rotation-coverage/checklist.md)
- monitoring-alerting.pipeline-liveness-and-runbook-reachability  (governance-commons/catalogs/concerns/monitoring-alerting/pipeline-liveness-and-runbook-reachability/checklist.md)
- monitoring-alerting.routing-and-escalation  (governance-commons/catalogs/concerns/monitoring-alerting/routing-and-escalation/checklist.md)

## observability
- observability.alerting-discipline  (governance-commons/catalogs/concerns/observability/alerting-discipline/checklist.md)
- observability.cardinality-discipline  (governance-commons/catalogs/concerns/observability/cardinality-discipline/checklist.md)
- observability.dashboard-discipline  (governance-commons/catalogs/concerns/observability/dashboard-discipline/checklist.md)
- observability.no-sensitive-data-in-telemetry  (governance-commons/catalogs/concerns/observability/no-sensitive-data-in-telemetry/checklist.md)
- observability.semantic-convention-coverage  (governance-commons/catalogs/concerns/observability/semantic-convention-coverage/checklist.md)
- observability.trace-context-propagation  (governance-commons/catalogs/concerns/observability/trace-context-propagation/checklist.md)

## performance-caching
- performance-caching.bounded-eviction  (governance-commons/catalogs/concerns/performance-caching/bounded-eviction/checklist.md)
- performance-caching.cache-as-optional  (governance-commons/catalogs/concerns/performance-caching/cache-as-optional/checklist.md)
- performance-caching.invalidation-strategy  (governance-commons/catalogs/concerns/performance-caching/invalidation-strategy/checklist.md)
- performance-caching.namespaced-keys  (governance-commons/catalogs/concerns/performance-caching/namespaced-keys/checklist.md)
- performance-caching.staleness-tolerance  (governance-commons/catalogs/concerns/performance-caching/staleness-tolerance/checklist.md)
- performance-caching.stampede-protection  (governance-commons/catalogs/concerns/performance-caching/stampede-protection/checklist.md)

## performance-database
- performance-database.bulk-operations  (governance-commons/catalogs/concerns/performance-database/bulk-operations/checklist.md)
- performance-database.index-alignment  (governance-commons/catalogs/concerns/performance-database/index-alignment/checklist.md)
- performance-database.keyset-pagination  (governance-commons/catalogs/concerns/performance-database/keyset-pagination/checklist.md)
- performance-database.pool-sizing  (governance-commons/catalogs/concerns/performance-database/pool-sizing/checklist.md)
- performance-database.pooled-connections  (governance-commons/catalogs/concerns/performance-database/pooled-connections/checklist.md)
- performance-database.replica-routing  (governance-commons/catalogs/concerns/performance-database/replica-routing/checklist.md)
- performance-database.transaction-scope  (governance-commons/catalogs/concerns/performance-database/transaction-scope/checklist.md)

## privacy
- privacy.data-subject-rights  (governance-commons/catalogs/concerns/privacy/data-subject-rights/checklist.md)
- privacy.lawful-basis-and-consent  (governance-commons/catalogs/concerns/privacy/lawful-basis-and-consent/checklist.md)
- privacy.no-personal-data-in-url  (governance-commons/catalogs/concerns/privacy/no-personal-data-in-url/checklist.md)
- privacy.personal-data-purpose-annotation  (governance-commons/catalogs/concerns/privacy/personal-data-purpose-annotation/checklist.md)
- privacy.processor-and-transfer-safeguards  (governance-commons/catalogs/concerns/privacy/processor-and-transfer-safeguards/checklist.md)
- privacy.purpose-limitation-and-minimization  (governance-commons/catalogs/concerns/privacy/purpose-limitation-and-minimization/checklist.md)
- privacy.retention-limitation  (governance-commons/catalogs/concerns/privacy/retention-limitation/checklist.md)

## reliability
- reliability.failure-isolation  (governance-commons/catalogs/concerns/reliability/failure-isolation/checklist.md)
- reliability.graceful-degradation  (governance-commons/catalogs/concerns/reliability/graceful-degradation/checklist.md)
- reliability.health-signaling  (governance-commons/catalogs/concerns/reliability/health-signaling/checklist.md)
- reliability.idempotency  (governance-commons/catalogs/concerns/reliability/idempotency/checklist.md)

## responsible-ai
- responsible-ai.ai-disclosure-marker  (governance-commons/catalogs/concerns/responsible-ai/ai-disclosure-marker/checklist.md)
- responsible-ai.data-governance  (governance-commons/catalogs/concerns/responsible-ai/data-governance/checklist.md)
- responsible-ai.decision-record-keeping  (governance-commons/catalogs/concerns/responsible-ai/decision-record-keeping/checklist.md)
- responsible-ai.explanation-and-recourse  (governance-commons/catalogs/concerns/responsible-ai/explanation-and-recourse/checklist.md)
- responsible-ai.fitness-evaluation  (governance-commons/catalogs/concerns/responsible-ai/fitness-evaluation/checklist.md)
- responsible-ai.model-documentation-artifact  (governance-commons/catalogs/concerns/responsible-ai/model-documentation-artifact/checklist.md)
- responsible-ai.model-provenance  (governance-commons/catalogs/concerns/responsible-ai/model-provenance/checklist.md)
- responsible-ai.output-safety  (governance-commons/catalogs/concerns/responsible-ai/output-safety/checklist.md)

## secrets-management
- secrets-management.encryption-at-rest  (governance-commons/catalogs/concerns/secrets-management/encryption-at-rest/checklist.md)
- secrets-management.least-privilege-access  (governance-commons/catalogs/concerns/secrets-management/least-privilege-access/checklist.md)
- secrets-management.no-secrets-in-logs  (governance-commons/catalogs/concerns/secrets-management/no-secrets-in-logs/checklist.md)
- secrets-management.rotation-policy  (governance-commons/catalogs/concerns/secrets-management/rotation-policy/checklist.md)
- secrets-management.runtime-retrieval  (governance-commons/catalogs/concerns/secrets-management/runtime-retrieval/checklist.md)

## supply-chain
- supply-chain.attestation-and-sbom-retention  (governance-commons/catalogs/concerns/supply-chain/attestation-and-sbom-retention/checklist.md)
- supply-chain.build-environment-isolation  (governance-commons/catalogs/concerns/supply-chain/build-environment-isolation/checklist.md)
- supply-chain.critical-dependency-audit  (governance-commons/catalogs/concerns/supply-chain/critical-dependency-audit/checklist.md)
- supply-chain.dependency-vetting  (governance-commons/catalogs/concerns/supply-chain/dependency-vetting/checklist.md)
- supply-chain.sbom-presence-and-validity  (governance-commons/catalogs/concerns/supply-chain/sbom-presence-and-validity/checklist.md)
- supply-chain.signed-commit-and-protected-branch  (governance-commons/catalogs/concerns/supply-chain/signed-commit-and-protected-branch/checklist.md)
- supply-chain.vulnerability-disclosure-response  (governance-commons/catalogs/concerns/supply-chain/vulnerability-disclosure-response/checklist.md)

## testing-strategy
- testing-strategy.critical-path-coverage  (governance-commons/catalogs/concerns/testing-strategy/critical-path-coverage/checklist.md)
- testing-strategy.deterministic-execution  (governance-commons/catalogs/concerns/testing-strategy/deterministic-execution/checklist.md)
- testing-strategy.test-pyramid-composition  (governance-commons/catalogs/concerns/testing-strategy/test-pyramid-composition/checklist.md)
