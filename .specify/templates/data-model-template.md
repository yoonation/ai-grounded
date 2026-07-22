# Data Model: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

<!--
  This artifact is instantiated from .specify/templates/data-model-template.md during
  plan Phase 1. Fill every section. The Normalization section is mandatory and is checked
  by tooling/data-model-normalization/check.py; leaving its TODO in place fails the gate.
-->

## Entities *(mandatory)*

<!--
  For each entity the feature introduces or touches, give:
  - Name
  - Fields (name and type or shape)
  - Relationships to other entities (by key)
  - Validation rules drawn from the requirements
  - State transitions, if the entity has a lifecycle
  Repeat the block per entity.
-->

### Entity: [EntityName]

- **Fields**: [field: type, field: type, ...]
- **Relationships**: [references [OtherEntity] by [key]; or none]
- **Validation rules**: [rule, rule, ...]
- **State transitions**: [state -> state on event; or none]

## Normalization *(mandatory)*

<!--
  State the single-source-of-truth decision for the data model, per the substrate rule
  code-organization.data-model-single-source-of-truth. For each entity, declare which
  fields are owned per-instance and which are constant across a referencing dimension
  (one value shared by every persona an operator owns, every order a customer places,
  every instance that shares a parent) and therefore live once on the referenced entity,
  referenced by key, not duplicated per-referrer. A deliberate duplicate is allowed if you
  record why; what is not allowed is skipping the decision.

  Example (replace with your own):
    Operator identity (name, email, phone) is constant across all of an operator's
    personas, so it lives once on Operator and Persona references it by operator_id.
    Persona-specific fields (tone, target_role) are owned per-instance on Persona.

  Replace the TODO below with the declaration for this feature's entities.
-->

TODO

---

<!--
  After filling this file, run:
    python3 tooling/data-model-normalization/check.py --path specs/[###-feature-name]/data-model.md --text
  The gate confirms the Normalization declaration is present and not a placeholder. It does
  not judge whether the decision is correct; staff-engineer reviews that at C2 against
  code-organization.data-model-single-source-of-truth.
-->
