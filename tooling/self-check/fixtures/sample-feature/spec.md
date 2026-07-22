# Feature Specification: candidate filtering

## What & Why

### User stories

#### User Story 1 - Filter by clearance (Priority: P1)

As a recruiter, I filter candidates by clearance level so I shortlist faster.

**Why this priority**: core to shortlisting; the MVP.

**Independent Test**: apply a clearance filter and confirm only matching candidates remain.

**Acceptance Scenarios**:

1. **Given** a pool with mixed clearances, **When** I filter by "secret", **Then** only secret-or-higher candidates show.
2. **Given** an active filter, **When** I clear it, **Then** all candidates return.

#### User Story 2 - Rank by match score (Priority: P2)

As a recruiter, I see filtered candidates ranked by match score.

**Why this priority**: speeds shortlisting after filtering.

**Independent Test**: filter, then confirm descending match-score order.

**Acceptance Scenarios**:

1. **Given** filtered candidates, **When** the list renders, **Then** they appear in descending match-score order.
