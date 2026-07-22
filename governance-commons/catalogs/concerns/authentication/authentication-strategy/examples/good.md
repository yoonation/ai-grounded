<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.authentication-strategy authentication strategy MADR (good)

A substrate-original example of a well-formed authentication
strategy MADR. The application described is fictional. The MADR
demonstrates the substrate's quality requirements for an L3 rule
decision document.

---

```markdown
# ADR-007: Authentication Strategy

## Status

Accepted

Date: 2026-04-15
Deciders: J. Park (CTO), M. Singh (Security Lead), R. Chen (Eng Lead)
Consulted: Security architecture review board; UX research team
Informed: All engineering; product management; customer support

## Context and Problem Statement

ExampleApp is launching as a consumer-facing personal finance
application. Users link banking, brokerage, and credit card
accounts; view consolidated balances and transactions; receive
budgeting recommendations. The application does not move money
between institutions (read-only aggregation).

User population: consumer (B2C); estimated 80% mobile-first usage;
target demographic 25-55; expected wide range of technical
sophistication. Geographic launch: US only initially; EU follow-on
in year 2.

Risk profile: high. Account compromise gives an attacker visibility
into the user's complete financial position including account
numbers (last 4 digits visible per Plaid-style aggregation),
transaction history, and balance trends. This is direct PII plus
financial-context PII. Regulated under GLBA in the US and GDPR for
the EU launch.

Identity infrastructure: greenfield. No existing IdP relationship
or legacy auth system to integrate with. Free choice.

Operational maturity: security team of 2 (lead plus engineer);
24/5 on-call coverage with paging for production issues; incident
response runbooks exist for breach and credential-stuffing
scenarios.

Recovery flow tolerance: low to moderate. Users locked out for
hours are likely to abandon (high-churn segment); users locked out
permanently will contact support and consume CS capacity at high
unit cost.

## Decision Drivers

D1. **Phishing resistance.** Financial aggregation applications are
prime phishing targets. Drivers from the threat model identify
phishing-via-fake-login as the highest-volume attack we should
expect.

D2. **Account recovery cost.** Customer support workload scales with
account-lockout incidents. Lower-friction recovery directly reduces
operational cost.

D3. **Mobile-first user population.** 80% mobile usage means our
auth choice must work fluidly on iOS and Android. Platform
authenticators are uniformly available on supported devices
(iOS 16+, Android 9+, which covers our target user devices).

D4. **No existing identity infrastructure.** We do not inherit
constraints from existing auth; we can choose freely.

D5. **Regulatory context.** GLBA Safeguards Rule and GDPR Article
32 both require authentication appropriate to the risk profile;
neither prescribes a specific method.

D6. **Time to market.** Six-week implementation window for the auth
surface. Strategies requiring extensive recovery-flow tooling will
not fit the window.

## Considered Options

1. Passkeys (WebAuthn) as primary, passwords as recovery factor
2. Passwords + mandatory MFA (TOTP)
3. Federated identity via Apple Sign In and Sign in with Google
4. Magic links (email-based passwordless)
5. Hybrid: passkeys primary, federated as alternative

## Decision Outcome

Chosen option: "Option 5 (Hybrid: passkeys primary, federated as
alternative)".

Reasoning: Option 1 (passkeys primary) directly addresses D1
(phishing resistance) and D3 (mobile-first works smoothly with
platform authenticators). Adding federated as an alternative
(specifically Sign in with Apple and Sign in with Google, the
two providers our user population already uses) addresses D2
(recovery cost) and D6 (time to market): users who lose all
passkeys can recover via the federated identity they already have
without bespoke recovery tooling. Federated also serves users
whose devices do not yet support platform authenticators.

We rejected Option 2 (password + MFA) because it produces the
largest substrate rule surface (all AUTH-L1 + most AUTH-L2 rules)
and does not fit the time-to-market driver D6. We rejected Option
3 (federated only) because it inherits hard dependency on
third-party IdP availability for our primary authentication path.
We rejected Option 4 (magic links) as inappropriate for the risk
profile (per substrate guidance on financial data).

### Substrate alignment

- Substrate-preferred option for this context: Option 1 (passkeys
  primary) per authentication.authentication-strategy decision-framework substrate analysis
- This decision: Option 5 (hybrid passkeys primary + federated
  alternative)
- Alignment status: Aligned (Option 5 includes Option 1 as the
  primary path; the federated alternative addresses recovery flow
  and unsupported-device scenarios that the substrate analysis
  acknowledges as Option 1 trade-offs)
- Substrate analysis acknowledges hybrid as substrate-acceptable
  with the caveat that the operational surface increases. This
  application accepts that trade-off because the secondary path
  (federated) is operationally well-understood and reduces
  recovery-flow tooling cost (D2 and D6).

## Consequences

### Positive consequences

- Phishing resistance achieved via the primary passkey path
  (D1 satisfied)
- Account recovery handled by the federated path with no bespoke
  recovery tooling needed (D2 satisfied; D6 satisfied)
- Mobile-first experience optimal on both supported platforms
  (D3 satisfied)
- Compliance posture: passkey + federated both meet GLBA
  Safeguards Rule "appropriate authentication" requirement; both
  acceptable under GDPR Article 32

### Negative consequences

- Hard dependency on Apple and Google as identity providers for
  the federated path; outage of either degrades recovery for
  affected users
- Two authentication paths to maintain and review (operational
  surface increase per substrate caveat on Option 5)
- Users without modern platform authenticators (older Android
  devices below 9, very old iOS devices) must use the federated
  path; some users may resist linking Apple or Google identity
  to a finance application

### Required follow-up work

Substrate rules in scope given this decision:

- authentication.mfa-on-privileged-operations (MFA on privileged operations) applies to both paths
- authentication.session-regeneration (session fixation prevention) applies to both paths
- authentication.mfa-enrollment (MFA enrollment hardening) applies to passkey
  enrollment specifically; addresses recovery code generation
  and storage
- authentication.no-credentials-in-urls, L1-003 (credentials not in URLs or logs) apply
  to federated callback handling
- authentication.rate-limiting (rate limiting) applies to both paths (login and
  recovery endpoints)

Substrate rules NOT in scope because passwords are not the primary
path:

- authentication.password-hashing (password storage hashing): not applicable; no
  passwords stored
- authentication.account-lockout (lockout policy): not applicable in the password
  sense; the equivalent for our paths is per-account rate
  limiting on the recovery flow (covered by authentication.rate-limiting)
- authentication.password-policy (password policy): not applicable

## Pros and Cons of the Options

### Option 1: Passkeys primary, passwords as recovery factor

- Good, because phishing-resistant (D1)
- Good, because aligned with FIDO and NIST modern guidance
- Good, because eliminates password concerns from the running
  application
- Bad, because passwords-as-recovery reintroduces the password
  rule surface partially (still must store password hashes;
  authentication.password-hashing applies)
- Bad, because recovery via password is itself phishable

### Option 2: Passwords + mandatory MFA

- Good, because operationally well-understood
- Good, because no third-party IdP dependency
- Bad, because phishable (D1 not satisfied)
- Bad, because largest substrate rule surface to implement
  correctly (D6 not satisfied; six-week window insufficient)
- Bad, because mobile user experience worse than passkey path
  (D3 partially not satisfied)

### Option 3: Federated only (Apple, Google)

- Good, because lowest implementation cost (D6 strongly satisfied)
- Good, because passes phishing resistance for users who use
  passkeys with their IdP (most do)
- Bad, because complete dependency on IdP availability for primary
  auth path
- Bad, because users who prefer not to link Apple/Google identity
  to a financial application have no alternative

### Option 4: Magic links

- Good, because zero password rule surface
- Good, because low user friction at login
- Bad, because auth strength tied to email security (often weak)
- Bad, because substrate explicitly does not recommend for
  financial data applications
- Bad, because email deliverability variance hurts user experience

### Option 5: Hybrid (passkeys primary, federated alternative)

- Good, because primary path is phishing-resistant (D1)
- Good, because federated handles recovery (D2 and D6)
- Good, because mobile-first user population well served (D3)
- Bad, because two authentication paths to maintain (operational
  surface)
- Bad, because IdP dependency for the recovery path

## References

- authentication.authentication-strategy (substrate rule for this decision)
- the authentication mechanical (L1) rules (mechanical rules; subset in
  scope per Consequences section)
- authentication.rate-limiting through authentication.mfa-enrollment (semantic rules; subset in
  scope)
- GLBA Safeguards Rule (16 CFR Part 314)
- GDPR Article 32 (security of processing)
- FIDO Alliance passkey deployment guidance

## Decision review schedule

- Next scheduled review: 2027-04-15 (annual)
- Triggers that force earlier review:
  - Either Apple or Google materially changes IdP terms or
    availability
  - User adoption of platform authenticators among the user
    population drops below 60% (operational telemetry threshold)
  - Material regulatory change affecting consumer financial
    authentication (CFPB, FTC, state-level financial-services
    requirements)
  - Any security incident affecting authentication
```

---

## Why this example is substrate-compliant

- MADR exists in the standard location
- Status is Accepted with date and deciders
- Context section is substantive: covers user population, risk
  profile, identity infrastructure, operational maturity, and
  recovery tolerance
- Decision drivers are concrete (D1-D6) and traceable to the
  application's actual context
- All 5 substrate-analyzed options are considered, with reasoning
  for rejection of each
- Chosen option is justified through driver-by-driver mapping
- Substrate alignment is explicit (Aligned with reasoning)
- Consequences include substrate-rule inventory in scope and
  out of scope
- Pros and cons are option-comparative
- Review schedule and triggers are defined

## Cross-reference

- Substrate rule: authentication.authentication-strategy in catalogs/concerns/authentication.oscal.yaml
- Decision framework binding: decision.md
- Review binding: checklist.md
- Anti-pattern: examples/authentication/authentication-strategy-anti-pattern.md
