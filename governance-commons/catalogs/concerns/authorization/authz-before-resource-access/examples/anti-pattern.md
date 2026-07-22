<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.authz-before-resource-access authorization decision precedes resource access (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Fetch first, check after (the canonical IDOR bug, Python / Django)

```python
# FORBIDDEN: resource fetched, then authorization checked.
# The fetch itself loads sensitive content into memory and may
# trigger application logging that reveals the resource exists.
def get_invoice_BAD(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)  # FETCH FIRST
    if invoice.owner_id != request.user.id:       # CHECK AFTER
        return HttpResponseForbidden()
    return JsonResponse(invoice.to_dict())
```

Why this violates authorization.authz-before-resource-access:
- The fetch happens regardless of authz outcome; cache and log
  side effects leak existence
- The "owner_id != user.id" check is naive: an admin role
  granting cross-owner access cannot be expressed
- Static analysis fires authorization.authz-before-resource-access on the order: Invoice
  .objects.get appears before the authorization comparison
- This is the most common IDOR pattern in production code

## Anti-pattern B: Authorization derived from resource content (Node.js)

```javascript
// FORBIDDEN: load the resource, then derive authorization
// from its content. A bug or race in the fetch leaks data
// before authorization runs.
app.get("/invoices/:id", async (req, res) => {
  const invoice = await Invoice.findById(req.params.id);  // FETCH
  if (!invoice) return res.status(404).end();
  if (invoice.ownerId !== req.user.id && req.user.role !== "admin") {
    return res.status(403).end();
  }
  res.json(invoice);
});
```

Why this violates authorization.authz-before-resource-access:
- Authorization input (ownerId) comes from the fetched
  resource; the fetch is decision-required
- The pattern produces an existence oracle: 404 versus 403 tells
  the attacker whether the invoice exists
- Adding more roles makes the inline check worse, not better;
  the centralized policy point (authorization.centralized-deny-by-default-policy) is the correct
  factoring

## Anti-pattern C: Loop fetches every resource, then filters (Python)

```python
# FORBIDDEN: fetch every invoice, then filter by ownership in
# application code. Worse than the per-resource version: every
# row's content reaches the application memory regardless of
# authz.
def list_invoices_BAD(request):
    all_invoices = Invoice.objects.all()  # FETCH EVERYTHING
    my_invoices = [
        inv for inv in all_invoices
        if inv.owner_id == request.user.id
    ]
    return JsonResponse([i.to_dict() for i in my_invoices], safe=False)
```

Why this violates authorization.authz-before-resource-access:
- All invoice rows are loaded into application memory before
  filtering; database connection logs and any inadvertent
  intermediate storage retain the unauthorized rows
- Scale failure: a system with 10 million invoices fetches all
  of them on every list request
- The substrate-recommended pattern is to push the authz filter
  into the query (Pattern B in the paired good-example file)
  via Row-Level Security or an explicit ORM .filter call

## Anti-pattern D: Authorization in a post-response hook (Java / Spring)

```java
// FORBIDDEN: response body assembled, authorization checked at
// a post-processing hook. The body has already been allocated
// and committed to the response stream by the time the hook
// runs.
@GetMapping("/invoices/{id}")
public Invoice getInvoice_BAD(@PathVariable String id, Authentication auth) {
    Invoice invoice = invoiceService.findById(id);  // FETCH
    return invoice;  // RETURN, framework runs hooks after
}

@Component
public class PostAuthzHook implements HandlerInterceptor {
    @Override
    public void postHandle(HttpServletRequest req, HttpServletResponse resp,
                          Object handler, ModelAndView mv) {
        // Too late: response committed.
    }
}
```

Why this violates authorization.authz-before-resource-access:
- Post-handler hooks run after the response body has been
  built and often after it has been committed
- The pattern's intent (centralize authz in a hook) is
  reasonable; the placement is wrong. The correct placement
  is a pre-handler interceptor, dependency, or guard that
  runs before the handler executes
