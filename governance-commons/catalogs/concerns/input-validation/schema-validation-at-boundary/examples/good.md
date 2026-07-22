<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.schema-validation-at-boundary schema validation at boundary

Substrate-original good patterns. Adapt to your stack.

## Pattern A: FastAPI with Pydantic v2

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal
import uuid

app = FastAPI()

class CreateOrderRequest(BaseModel):
    # Strict mode rejects unknown fields.
    model_config = ConfigDict(extra="forbid")

    customer_id: uuid.UUID
    email: EmailStr
    quantity: int = Field(ge=1, le=10000)
    item_sku: str = Field(min_length=3, max_length=20, pattern=r"^[A-Z0-9-]+$")
    priority: Literal["standard", "express", "overnight"] = "standard"

@app.post("/orders")
def create_order(request: CreateOrderRequest):
    # request is fully typed; no isinstance checks needed.
    # request.customer_id is a uuid.UUID, not a str.
    return OrderService.create(request)
```

The schema declares: required vs optional, domain types,
length and range constraints, enumerated values, regex
patterns. Strict mode rejects unknown fields.

## Pattern B: Express with Joi middleware

```javascript
const Joi = require('joi');

const createOrderSchema = Joi.object({
  customer_id: Joi.string().uuid().required(),
  email: Joi.string().email().required(),
  quantity: Joi.number().integer().min(1).max(10000).required(),
  item_sku: Joi.string().pattern(/^[A-Z0-9-]+$/).min(3).max(20).required(),
  priority: Joi.string().valid('standard', 'express', 'overnight').default('standard'),
}).unknown(false);  // reject unknown fields

const validate = (schema) => (req, res, next) => {
  const { error, value } = schema.validate(req.body, { abortEarly: false });
  if (error) {
    return res.status(400).json({
      type: 'urn:problem:validation-error',
      errors: error.details.map(d => ({ field: d.path.join('.'), message: d.message })),
    });
  }
  req.validatedBody = value;
  next();
};

app.post('/orders', validate(createOrderSchema), (req, res) => {
  // req.validatedBody is the parsed, validated payload.
  OrderService.create(req.validatedBody).then(result => res.json(result));
});
```

## Pattern C: Spring Boot with Jakarta Bean Validation

```java
public record CreateOrderRequest(
    @NotNull UUID customerId,
    @NotBlank @Email String email,
    @Min(1) @Max(10000) int quantity,
    @NotBlank @Pattern(regexp = "^[A-Z0-9-]+$") @Size(min = 3, max = 20) String itemSku,
    @NotNull OrderPriority priority
) {}

@RestController
public class OrderController {
    @PostMapping("/orders")
    public Order createOrder(@Valid @RequestBody CreateOrderRequest request) {
        // request is fully validated by the time the handler runs.
        return orderService.create(request);
    }
}
```

## Pattern D: Zod schema with TypeScript inference

```typescript
import { z } from 'zod';

const CreateOrderSchema = z.object({
  customer_id: z.string().uuid(),
  email: z.string().email(),
  quantity: z.number().int().min(1).max(10000),
  item_sku: z.string().regex(/^[A-Z0-9-]+$/).min(3).max(20),
  priority: z.enum(['standard', 'express', 'overnight']).default('standard'),
}).strict();  // reject unknown fields

type CreateOrderRequest = z.infer<typeof CreateOrderSchema>;

app.post('/orders', async (req, res) => {
  const result = CreateOrderSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({
      type: 'urn:problem:validation-error',
      errors: result.error.issues,
    });
  }
  const order = await OrderService.create(result.data);
  res.json(order);
});
```

The TypeScript type for `CreateOrderRequest` is inferred from
the schema, so the schema and the type stay in sync by
construction.
