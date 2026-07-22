<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.object-level-authorization object-level authorization (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: No per-resource check; authenticated is treated as authorized (Python)

```python
# FORBIDDEN: any authenticated user can access any invoice
# by guessing or enumerating IDs.
@login_required
def get_invoice_BAD(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)
    return JsonResponse(invoice.to_dict())
```

Why this violates authorization.object-level-authorization:
- Canonical IDOR pattern
- @login_required only authenticates; does not authorize
- Sequential integer IDs make exploitation trivial; UUIDs slow
  it but do not stop it

## Anti-pattern B: Ownership check via request body field (Node.js)

```javascript
// FORBIDDEN: the request body says owner_id and the server
// trusts it. Attacker submits a body matching their own ID
// even though the invoice belongs to someone else.
app.get("/invoices/:id", async (req, res) => {
  const invoice = await Invoice.findById(req.params.id);
  if (invoice.ownerId !== req.body.owner_id) {  // client supplies owner_id
    return res.status(403).end();
  }
  res.json(invoice);
});
```

Why this violates authorization.object-level-authorization:
- The authorization input comes from the client; the attacker
  controls it
- The comparison is meaningless: the attacker submits any
  value to make it equal
- Substrate-required source of principal identity is the
  authoritative session, not request fields

## Anti-pattern C: Filter by resource property after fetch (Python)

```python
# FORBIDDEN: list endpoint fetches all invoices then filters
# in application code. A bug in the filter leaks data.
def list_invoices_BAD(request):
    all_invoices = Invoice.objects.all()
    visible = [
        inv for inv in all_invoices
        if inv.owner_id == request.user.id
        or inv.shared_with(request.user)
        or request.user.is_admin
    ]
    return JsonResponse([i.to_dict() for i in visible], safe=False)
```

Why this violates authorization.object-level-authorization:
- Every invoice row is loaded into application memory
- A bug in the filter (a missing condition, an off-by-one,
  an inverted check) leaks invoices
- The substrate-recommended fix is to push the filter into the
  query: Invoice.objects.filter(...) with conditions, or RLS

## Anti-pattern D: Bulk endpoint authorizes the request, not each resource (Python)

```python
# FORBIDDEN: the bulk endpoint checks "may principal access
# invoices at all", not "may principal access THIS invoice".
@app.post("/invoices/batch")
def batch_BAD(request):
    if not request.user.has_role("read-invoices"):
        return HttpResponseForbidden()

    ids = request.json["ids"]
    invoices = Invoice.objects.filter(id__in=ids)  # NO PER-RESOURCE CHECK
    return JsonResponse([i.to_dict() for i in invoices], safe=False)
```

Why this violates authorization.object-level-authorization:
- The role check authorizes the endpoint, not each invoice
- A principal with "read-invoices" role can read any invoice,
  not just their own
- The pattern is a common authorization gap because reviewers
  see the role check and think the endpoint is protected;
  the per-resource check is the substrate's L2-001 requirement

## Anti-pattern E: Slug-based resource access without authz (Python)

```python
# FORBIDDEN: the URL contains a slug rather than an ID. Many
# teams assume slugs are "obscure" and skip authorization.
@app.route("/docs/<slug>")
def get_document_BAD(slug):
    doc = Document.objects.filter(slug=slug).first()
    if not doc:
        return HttpResponseNotFound()
    return JsonResponse(doc.to_dict())
```

Why this violates authorization.object-level-authorization:
- Slugs are not authorization; they are convenience identifiers
- Slug enumeration (dictionary words, names, leaked references)
  succeeds against this pattern
- The substrate's L2-001 requirement applies to all resource
  identifier types: numeric IDs, UUIDs, slugs, ARNs, file paths
