# Testing Quality Scorecard

This scorecard complements line coverage with behavior-focused indicators.

## Why

Line coverage answers: "Did code run?"

This scorecard answers: "Would tests catch bad behavior?"

## Current Baseline (2026-04-17)

- Full-suite line coverage: 41%
- Critical auth behavior coverage:
  - accounts/views/auth.py: 98%
  - accounts/views/user.py: 97%
- Core shared view mixin coverage:
  - utils/views/base.py: 98%

## Behavior Quality Metrics

Use these together. No single metric is enough.

### 1) Risk-Weighted Coverage

Track coverage only for high-risk modules first (auth, permission, shift lifecycle).

Suggested risk tiers:

- Tier 1 (critical): authentication, authorization, user identity, participation permissions
- Tier 2 (important): shift creation/update/delete and recurring generation
- Tier 3 (supporting): helpers and UI integration

### 2) Scenario Coverage

Maintain a behavior matrix and mark each scenario as:

- Covered: at least one deterministic automated test
- Partial: path exists but edge/error branches missing
- Missing: no automated coverage

#### Scenario Matrix

| Domain | Scenario | Status | Test Reference |
|---|---|---|---|
| Auth | Local login rendering and fallback flows | Covered | `accounts/tests/test_auth_views.py` |
| Auth | SSO login initiation (enabled/disabled) | Covered | `accounts/tests/test_auth_views.py` |
| Auth | OAuth callback success/failure/exception | Covered | `accounts/tests/test_auth_views.py` |
| Auth | Confirm-email valid/invalid/malformed token paths | Covered | `accounts/tests/test_user_views.py` |
| Auth | Logout and relogin cache/session edge behavior | Partial | `accounts/tests/test_auth_views.py` |
| Auth | Password-reset confirmation invalid/expired token behavior | Missing | `n/a` |
| Auth | Brute-force and repeated failed-login throttling behavior | Missing | `n/a` |
| Permissions | Missing-permission behavior (redirect, 403, fail URL) | Covered | `utils/tests/test_base_views.py` |
| Permissions | Shift participation permission update workflow | Covered | `shifts/tests/test_permission_views.py` |
| Permissions | Duplicate organization rejection in permission formset | Covered | `shifts/tests/test_permission_forms.py` |
| Permissions | Cross-organization isolation for permission edits | Missing | `n/a` |
| Permissions | Permission precedence conflicts across global/org scopes | Partial | `shifts/tests/test_permission_forms.py` |
| Shifts | Participant add/remove for self and others | Covered | `shifts/tests/test_participant_views.py` |
| Shifts | Shift CRUD edge cases (date bounds, authz, redirects) | Partial | `shifts/tests/*` |
| Shifts | Summary view filtering and boundary scenarios | Missing | `n/a` |
| Shifts | Concurrent participant slot contention and max-user enforcement | Missing | `n/a` |
| Shifts | Shift copy/template creation with invalid source references | Missing | `n/a` |
| Recurring shifts | Form validation for recurring setup | Partial | `shifts/tests/*` |
| Recurring shifts | Recurring generation command and date edge cases | Missing | `n/a` |
| Recurring shifts | Timezone and DST boundary generation correctness | Missing | `n/a` |
| Recurring shifts | Idempotency of repeated recurring generation runs | Missing | `n/a` |
| Mail | Attachment size and date-range validation | Covered | `mail/tests/test_mail_forms.py` |
| Mail | Mail view send flows and permission boundaries | Partial | `mail/tests/*` |
| Mail | Delivery failure/retry behavior and user-visible error states | Missing | `n/a` |
| Mail | Recipient resolution with mixed member/group filters | Partial | `mail/tests/*` |
| Utils | Protected media header dispatch by backend type | Covered | `utils/tests/test_protected_content.py` |
| Utils | Saved-path breadcrumb behavior with complex query params | Partial | `utils/tests/test_base_views.py` |
| Utils | Http403 middleware integration and custom error page wiring | Missing | `n/a` |

### 3) Mutation Score (Recommended)

Measure if tests fail when implementation is intentionally perturbed.

Target:

- Tier 1 modules: > 70%
- Tier 2 modules: > 55%

Note:

- Start with small scope to keep runtime manageable.
- Prioritize accounts/views/auth.py, utils/views/base.py, shifts/views/shift.py.

### 4) Regression Protection Index

For each bug fix, add a test that fails before the fix.

Track monthly:

- Bugs fixed with regression test / total bugs fixed

Target:

- 100% for Tier 1 bugs

## Scorecard Template

Update this table in each release cycle.

| Metric | Current | Target | Trend |
|---|---:|---:|---|
| Full-suite line coverage | 41% | 50% | up |
| Tier 1 weighted coverage | n/a | 75% | n/a |
| Scenario coverage (Tier 1) | 8/13 | 10/13 | up |
| Mutation score (Tier 1) | n/a | 70% | n/a |
| Regression protection index (Tier 1) | n/a | 100% | n/a |

## Update Procedure

1. Run full tests with coverage.
2. Update Tier 1/Tier 2 module coverage values.
3. Review scenario matrix and mark new covered paths.
4. Record newly fixed bugs and whether regression tests exist.
5. Update scorecard table and share in release notes.
