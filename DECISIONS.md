# Development Decisions

## Key Decisions

### 1. Data Ingestion
**Flexible column aliasing** over strict schema validation to handle varying CSV formats.

### 2. Unit Normalization
**Normalize to MWh (energy) and thousand dollars (cost)** for consistent comparison.

### 3. Validation
**Flag for review** rather than reject - suspicious data may be valid.

### 4. Multi-tenancy
**User-based isolation** - sufficient for single-organization deployments.

### 5. Audit Trail
**Preserve complete raw data** and all transformation logs.

### 6. Authentication
**Token-based** with Django REST Framework - simple and stateless.

### 7. Deployment
**Separate frontend (Vercel) and backend (Render)** for independent scaling.

## Questions for PM
- Should we support custom column mapping per customer?
- What's the acceptable false positive rate for warnings?
- Do we need true multi-tenancy (multiple organizations)?
- Should we support SSO (SAML/OAuth)?