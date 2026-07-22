<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.no-hardcoded-role-strings no hardcoded role or permission strings in business logic (good patterns)

Substrate-original good-pattern examples for authorization.no-hardcoded-role-strings.

## Pattern A: Cedar policy with code that asks the policy point (Python)

```python
# Business logic asks the policy point for a decision. The
# string "admin" or "editor" never appears in business code;
# the role concept lives in the Cedar policy file.
from app.authz import policy_point


def archive_report(principal, report_id):
    decision = policy_point.decide(
        principal=principal,
        action="archive",
        resource_type="report",
        resource_id=report_id,
    )
    if decision.allow is not True:
        raise PermissionDenied()
    perform_archive(report_id)
```

```cedar
// policies/reports.cedar - the policy as data
permit (
    principal in Role::"editor",
    action == Action::"archive",
    resource is Report
) when {
    resource.owner == principal
        || resource.status == "draft"
};

permit (
    principal in Role::"admin",
    action == Action::"archive",
    resource is Report
);
```

## Pattern B: OPA Rego policy externalized (Python)

```python
import requests


def check_permission(principal_id, action, resource_id):
    """Ask OPA whether the action is permitted."""
    response = requests.post(
        "http://opa.internal:8181/v1/data/authz/allow",
        json={
            "input": {
                "principal": principal_id,
                "action": action,
                "resource": resource_id,
            }
        },
        timeout=2,
    )
    return response.json().get("result", False)


def archive_report(principal_id, report_id):
    if not check_permission(principal_id, "archive", report_id):
        raise PermissionDenied()
    perform_archive(report_id)
```

```rego
# policies/authz.rego - all role logic lives here
package authz

default allow = false

allow {
    input.action == "archive"
    role := data.principals[input.principal].role
    role == "editor"
    owner := data.resources[input.resource].owner
    owner == input.principal
}

allow {
    input.action == "archive"
    role := data.principals[input.principal].role
    role == "admin"
}
```

## Pattern C: Pundit policy classes (Ruby / Rails)

```ruby
# app/policies/report_policy.rb - role logic lives here
class ReportPolicy < ApplicationPolicy
  def archive?
    user.admin? || (user.editor? && record.draft?)
  end
end


# app/controllers/reports_controller.rb - business logic
# delegates to policy
class ReportsController < ApplicationController
  def archive
    @report = Report.find(params[:id])
    authorize @report, :archive?  # Pundit consults ReportPolicy
    @report.archive!
    redirect_to reports_path
  end
end
```

The User model knows about `admin?` and `editor?`. Application
controllers do not embed string comparisons.

## Pattern D: django-guardian object permissions (Python / Django)

```python
from guardian.shortcuts import get_perms


def archive_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if "archive_report" not in get_perms(request.user, report):
        raise PermissionDenied()
    report.archive()
    return redirect("report_list")
```

Permissions are stored in the database and granted to users
explicitly. The action name "archive_report" is a permission
constant, not a hardcoded role string.

Why these patterns satisfy authorization.no-hardcoded-role-strings:
- No literal role string ("admin", "editor", "viewer") appears
  in business logic
- Role and permission decisions are made by the policy point
  (Cedar engine, OPA, Pundit policy class, django-guardian)
- Adding, renaming, or removing a role does not require
  changing business code
- Static analysis fires only on inline string comparisons in
  business logic; policy file content and User model role-
  recognition helpers are out of scope per authorization.no-hardcoded-role-strings
