<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.centralized-deny-by-default-policy centralized deny-by-default policy (good patterns)

Substrate-original good-pattern examples for authorization.centralized-deny-by-default-policy.

## Pattern A: Single Cedar policy engine, every endpoint asks (Python)

```python
import cedar_engine

# One engine instance, loaded from policy files at startup
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = cedar_engine.Engine(
            policies=glob.glob("policies/*.cedar"),
            schema="policies/schema.json",
        )
    return _engine


class PolicyPoint:
    """The single authority for authorization decisions."""

    def decide(self, principal, action, resource_type, resource_id=None):
        engine = get_engine()
        result = engine.is_authorized(
            principal=f"Role::{principal.role}::{principal.subject_id}",
            action=f"Action::{action}",
            resource=f"Resource::{resource_type}::{resource_id or '*'}",
            context={
                "tenant_id": str(principal.tenant_id),
                "time": now().isoformat(),
            },
        )
        # Cedar returns "Allow" or "Deny"; treat unrecognized
        # results as Deny (deny-by-default)
        allow = (result == "Allow")
        return Decision(
            allow=allow,
            reason=result if allow else "deny-by-default",
        )
```

Every authorization decision in the application flows through
PolicyPoint.decide. Policy lives in Cedar files external to
code; changes to policy do not require code changes.

## Pattern B: Open Policy Agent (OPA) as centralized engine

```python
import requests


class OPAClient:
    """Centralized policy point implemented as OPA client."""

    def __init__(self, opa_url="http://opa:8181"):
        self.opa_url = opa_url

    def decide(self, principal, action, resource_type, resource_id=None):
        response = requests.post(
            f"{self.opa_url}/v1/data/authz/allow",
            json={
                "input": {
                    "principal": {
                        "subject_id": principal.subject_id,
                        "role": principal.role,
                        "tenant_id": str(principal.tenant_id),
                    },
                    "action": action,
                    "resource": {
                        "type": resource_type,
                        "id": resource_id,
                    },
                }
            },
            timeout=2,
        )
        # Deny-by-default: any unparseable response or absent
        # "result" treated as deny
        try:
            result = response.json().get("result", False)
        except (ValueError, AttributeError):
            return Decision(allow=False, reason="opa-error")
        return Decision(
            allow=(result is True),
            reason="allow" if result else "deny-by-default",
        )
```

```rego
# policies/authz.rego - all authorization logic in one place
package authz

default allow = false  # DENY-BY-DEFAULT

allow {
    input.action == "read"
    input.resource.type == "invoice"
    invoice := data.invoices[input.resource.id]
    invoice.owner_id == input.principal.subject_id
}

allow {
    input.action == "read"
    input.resource.type == "invoice"
    input.principal.role == "admin"
}

# Add more allow rules; default of false ensures unknown
# combinations deny
```

## Pattern C: Pundit with explicit deny-by-default base policy (Ruby)

```ruby
# app/policies/application_policy.rb - default deny base
class ApplicationPolicy
  attr_reader :user, :record

  def initialize(user, record)
    @user = user
    @record = record
  end

  # Every action defaults to false. Concrete policies must
  # explicitly override to grant.
  def index?;   false; end
  def show?;    false; end
  def create?;  false; end
  def update?;  false; end
  def destroy?; false; end
end


# app/policies/invoice_policy.rb - explicit grants
class InvoicePolicy < ApplicationPolicy
  def show?
    user.admin? || record.owner == user
  end

  def create?
    user.editor? || user.admin?
  end

  # update? and destroy? inherited as false (deny-by-default)
end
```

## Pattern D: Policy unit-tested as data

```python
# tests/test_policies.py - load production policies into test
# engine and assert decisions
import pytest
import cedar_engine


@pytest.fixture(scope="session")
def policy_engine():
    return cedar_engine.Engine(
        policies=glob.glob("policies/*.cedar"),
        schema="policies/schema.json",
    )


def test_admin_can_read_any_invoice(policy_engine):
    decision = policy_engine.is_authorized(
        principal="Role::admin::user_001",
        action="Action::read",
        resource="Resource::invoice::inv_999",
    )
    assert decision == "Allow"


def test_editor_can_read_own_invoice(policy_engine):
    decision = policy_engine.is_authorized(
        principal="Role::editor::user_002",
        action="Action::read",
        resource="Resource::invoice::inv_002",
        context={"resource_owner": "user_002"},
    )
    assert decision == "Allow"


def test_unknown_action_denies(policy_engine):
    decision = policy_engine.is_authorized(
        principal="Role::admin::user_001",
        action="Action::cosmic_ray",  # not in vocabulary
        resource="Resource::invoice::inv_001",
    )
    assert decision == "Deny"


def test_malformed_input_denies(policy_engine):
    decision = policy_engine.is_authorized(
        principal="malformed",
        action="Action::read",
        resource="Resource::invoice::inv_001",
    )
    assert decision == "Deny"
```

Policies are testable independent of the web framework, the
database, and any other runtime component. The CI pipeline
runs these tests on every policy change.

Why these patterns satisfy authorization.centralized-deny-by-default-policy:
- One policy point with a known API; every call site uses it
- Policy expressed as data (Cedar files, Rego files, policy
  classes) external to business logic
- Deny-by-default at the engine level: unknown subjects,
  actions, or resources return Deny without exception
- Policy is unit-testable as data, enabling CI gate on policy
  correctness
- Adding a new role or permission happens in policy files;
  business code does not change
