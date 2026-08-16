# Tenant Module

## Entities

### Tenant

Represents a customer workspace (subscription owner).

Fields:

- id
- name
- slug
- is_active
- created_at
- updated_at

---

### Company

Represents a legal company owned by a tenant.

Relationship:

Tenant (1) -----> Company (N)

Fields:

- id
- tenant
- name
- code
- is_active
- created_at
- updated_at

Constraints:

- Company code must be unique within the same tenant.

---

## Membership

Represents a user's membership within a tenant.

### Relationships

Tenant (1) --------< Membership >-------- (1) User

### Fields

- id
- tenant
- user
- is_active
- joined_at

### Constraints

- A user cannot have more than one membership in the same tenant.

### Notes

Membership represents only the user's association with the tenant.

Authorization (Roles & Permissions) will be implemented separately.

## TenantMiddleware

### Purpose

Builds the tenant context for every authenticated request.

### Current Status (Stage 3.4.2)

Current responsibilities:

- Initialize:
  - `request.tenant`
  - `request.membership`
  - `request.company`

- Skip anonymous requests.

### Next Step

Resolve the active Membership and populate the tenant context.

### Current Status (Stage 3.4.3)

Current responsibilities:

- Initialize tenant context.
- Skip anonymous users.
- Resolve the active Membership using `get_current_membership()`.

The resolved membership is not yet attached to the request object.

## Tenant Context

### TenantContext Service

The tenant context resolution has been extracted into a dedicated service.

Responsibilities:

- Initialize request context.
- Resolve the authenticated user's membership.
- Attach:
  - request.membership
  - request.tenant
  - request.company (reserved for future implementation)

This service is designed to be consumed by the DRF layer rather than Django middleware.

### TenantContextMixin

The `TenantContextMixin` integrates tenant context resolution into Django REST Framework.

Execution flow:

Request
    â†“
JWT Authentication
    â†“
TenantContextMixin.initial()
    â†“
TenantContext.resolve()
    â†“
request.membership
request.tenant
request.company

## Tenant Context Resolution

### Previous Approach

The project initially attempted to resolve the tenant using a Django middleware.

This approach failed because JWT authentication in Django REST Framework occurs after the Django middleware phase, making `request.user` unavailable during middleware execution.

### Current Approach

Tenant context is resolved inside the DRF request lifecycle using `TenantContextMixin`.

Execution flow:

HTTP Request
    â†“
JWT Authentication
    â†“
TenantContextMixin.initial()
    â†“
TenantContext.resolve()
    â†“
request.membership
request.tenant
request.company
    â†“
APIView

### Advantages

- Fully compatible with JWT authentication.
- Keeps business logic outside API views.
- Reusable across APIView, GenericAPIView and ViewSets.
- Easier to test and maintain.

### Middleware Removal

The original `TenantMiddleware` implementation has been removed.

Reason:

- Django middleware executes before DRF JWT authentication.
- Therefore, `request.user` is not available for authenticated JWT requests.
- Tenant resolution is now handled exclusively by `TenantContextMixin`.

## Tenant-Aware Membership Resolution

### Stage 3.6.1 — Tenant-Aware Membership Resolution

The tenant context resolution was enhanced to support users who belong to multiple tenants.

`get_current_membership()` now follows these rules:

* Returns the active Membership when the user has exactly one active membership.
* Requires the related Tenant to also be active.
* Returns `None` when the user has multiple active memberships.
* Returns `None` when the user has no valid active membership.
* Does not implicitly select the first tenant.

This prevents the application from making an unsafe tenant selection when a user belongs to multiple tenants.

---

### Stage 3.6.2 — Tenant-Aware Membership Services

A dedicated service was introduced for resolving an explicitly selected tenant:

`get_membership_for_tenant(user, tenant_id)`

The service:

* Requires an authenticated user.
* Searches only for the specified tenant.
* Requires an active Membership.
* Requires the selected Tenant to be active.
* Returns `None` when the user does not belong to the selected tenant.
* Returns `None` when the selected tenant does not exist or is inactive.

This keeps tenant-selection logic outside API views and provides a reusable service for future tenant-aware features.

---

### Stage 3.6.3 — Explicit Tenant Selection

Explicit tenant selection was integrated into the DRF tenant context flow.

The API accepts the selected tenant through the HTTP header:

`X-Tenant-ID`

The request flow is now:

HTTP Request
↓
JWT Authentication
↓
TenantContextMixin.perform_authentication()
↓
Read X-Tenant-ID
↓
TenantContext.resolve()
↓
get_membership_for_tenant()
↓
request.membership
request.tenant
request.company
↓
IsTenantMember
↓
APIView

When `X-Tenant-ID` is not provided:

* A tenant is selected automatically only when the user has exactly one active tenant membership.
* No tenant is selected when the user belongs to multiple active tenants.

When `X-Tenant-ID` is provided:

* The tenant must exist.
* The tenant must be active.
* The authenticated user must have an active membership in that tenant.
* Otherwise, tenant context remains unresolved and tenant-aware permissions deny access.

---

### Stage 3.6.4 — Tenant Isolation in Company API

Tenant isolation was enforced in the Company API.

The Company API now operates against the currently resolved tenant context.

The following behavior is enforced:

* Users can only list companies belonging to their current tenant.
* Users can only retrieve companies belonging to their current tenant.
* Users can only update companies belonging to their current tenant.
* Users can only delete companies belonging to their current tenant.
* Newly created companies are automatically assigned to the current tenant.
* Client-provided tenant values cannot override the resolved tenant.
* Attempting to access a company belonging to another tenant returns `404 Not Found`.
* Attempting to modify or delete a company belonging to another tenant returns `404 Not Found`.

This establishes the first concrete tenant-isolation boundary for tenant-owned business data.

---

## Tenant Selection and Isolation Rules

The current architecture follows these rules:

### Single-Tenant User

If a user has exactly one active membership:

* The tenant is resolved automatically.
* No `X-Tenant-ID` header is required.

### Multi-Tenant User

If a user has multiple active memberships:

* No tenant is selected implicitly.
* The user must provide `X-Tenant-ID`.
* The selected tenant must belong to the user.
* The selected tenant must be active.

### Unauthorized Tenant Selection

If the user provides a tenant ID for:

* A tenant they do not belong to.
* An inactive tenant.
* A nonexistent tenant.

The tenant context is not resolved and tenant-aware access is denied.

### Tenant-Owned Data

Tenant-owned resources must always be filtered through the resolved tenant context.

For Company:

```text
Authenticated User
        ↓
Resolved Tenant
        ↓
Company Query
        ↓
Only Companies belonging to Resolved Tenant
```

The client must never be trusted to determine the tenant ownership of newly created or modified tenant-owned records.

---

## Testing

Automated tests cover the tenant selection and isolation behavior introduced in Stage 3.6.

### Tenant Context Tests

The Tenant Context tests verify:

* Single active tenant resolution.
* Multiple active tenant memberships do not cause implicit tenant selection.
* Explicit tenant selection through `tenant_id`.
* Rejection of a tenant without membership.
* Rejection of an inactive tenant.
* Rejection of unauthenticated users.
* Request context isolation.

### Tenant Context API Tests

The Tenant Context API tests verify:

* Authenticated access.
* Authentication requirements.
* Multiple-tenant behavior.
* Explicit tenant selection through `X-Tenant-ID`.
* Rejection of a tenant without membership.
* Rejection of an inactive tenant.
* Rejection of a nonexistent tenant.

### Company API Tests

The Company API tests verify:

* Company listing is restricted to the current tenant.
* Company retrieval is restricted to the current tenant.
* Company creation assigns the resolved tenant.
* Client tenant override is prevented.
* Company updates are restricted to the current tenant.
* Company deletion is restricted to the current tenant.
* Explicit tenant selection changes the visible company scope.
* Selecting a tenant without membership is denied.

### Latest Test Result

```text
Found 39 test(s).
.......................................

Ran 39 tests

OK
```

All tenant module tests pass successfully.

---

## Current Tenant Architecture

The current tenant-aware request flow is:

```text
HTTP Request
    ↓
JWT Authentication
    ↓
TenantContextMixin.perform_authentication()
    ↓
Read X-Tenant-ID
    ↓
TenantContext.resolve()
    ↓
Membership Resolution
    ↓
request.membership
request.tenant
request.company
    ↓
IsTenantMember
    ↓
Tenant-Aware API
    ↓
Tenant-Isolated Data
```

The current implementation provides explicit tenant selection and the first enforced tenant-isolation boundary through the Company API.
