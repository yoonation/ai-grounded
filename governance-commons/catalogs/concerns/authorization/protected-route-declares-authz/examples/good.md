<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.protected-route-declares-authz protected route declares server-side authorization (good patterns)

Substrate-original good-pattern examples for authorization.protected-route-declares-authz.

## Pattern A: Flask with explicit decorator (Python / Flask)

```python
from flask import Flask, request, abort
from app.authz import policy_point, current_principal

app = Flask(__name__)


def requires_permission(action, resource_type):
    """Authorization decorator. Every protected route uses this."""
    def decorator(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*args, **kwargs):
            principal = current_principal()
            decision = policy_point.decide(
                principal=principal,
                action=action,
                resource_type=resource_type,
                resource_id=kwargs.get("id"),
            )
            if decision.allow is not True:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/reports/<id>")
@requires_permission(action="read", resource_type="report")
def get_report(id):
    return fetch_report(id).to_json()


@app.route("/reports/<id>", methods=["DELETE"])
@requires_permission(action="delete", resource_type="report")
def delete_report(id):
    delete_report_record(id)
    return "", 204
```

## Pattern B: FastAPI with dependency injection (Python / FastAPI)

```python
from fastapi import FastAPI, Depends, HTTPException
from app.authz import policy_point
from app.session import current_principal_dep

app = FastAPI()


def require_authz(action: str, resource_type: str):
    """Dependency factory for FastAPI route protection."""
    def _check(
        principal=Depends(current_principal_dep),
        resource_id: str = None,
    ):
        decision = policy_point.decide(
            principal=principal,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        if decision.allow is not True:
            raise HTTPException(status_code=403)
        return principal
    return _check


@app.get("/reports/{resource_id}")
def get_report(
    resource_id: str,
    _=Depends(require_authz("read", "report")),
):
    return fetch_report(resource_id).to_dict()


@app.delete("/reports/{resource_id}")
def delete_report(
    resource_id: str,
    _=Depends(require_authz("delete", "report")),
):
    delete_report_record(resource_id)
```

## Pattern C: Express with router-level middleware (Node.js / Express)

```javascript
const express = require("express");
const { policyPoint, currentPrincipal } = require("./authz");

const router = express.Router();


function requiresPermission(action, resourceType) {
  return async (req, res, next) => {
    const principal = currentPrincipal(req);
    const decision = await policyPoint.decide({
      principal,
      action,
      resourceType,
      resourceId: req.params.id,
    });
    if (decision.allow !== true) {
      return res.status(403).end();
    }
    next();
  };
}


router.get(
  "/reports/:id",
  requiresPermission("read", "report"),
  async (req, res) => {
    const report = await fetchReport(req.params.id);
    res.json(report);
  }
);

router.delete(
  "/reports/:id",
  requiresPermission("delete", "report"),
  async (req, res) => {
    await deleteReport(req.params.id);
    res.status(204).end();
  }
);

module.exports = router;
```

## Pattern D: Spring Security with method security (Java / Spring)

```java
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/reports")
public class ReportController {

    @GetMapping("/{id}")
    @PreAuthorize("@policyPoint.canRead(#id, authentication)")
    public Report getReport(@PathVariable String id) {
        return reportService.findById(id);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("@policyPoint.canDelete(#id, authentication)")
    public void deleteReport(@PathVariable String id) {
        reportService.delete(id);
    }
}
```

Why these patterns satisfy authorization.protected-route-declares-authz:
- Every route handler that returns or modifies a resource is
  guarded by an explicit authorization construct at the
  declaration site
- The authorization decision flows through a centralized policy
  point (consistent with authorization.centralized-deny-by-default-policy)
- The construct is detectable by static analysis: a route
  declaration without the decorator, dependency, middleware, or
  annotation fails the L1 scan
