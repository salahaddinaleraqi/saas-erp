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
    ↓
JWT Authentication
    ↓
TenantContextMixin.initial()
    ↓
TenantContext.resolve()
    ↓
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
    ↓
JWT Authentication
    ↓
TenantContextMixin.initial()
    ↓
TenantContext.resolve()
    ↓
request.membership
request.tenant
request.company
    ↓
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

