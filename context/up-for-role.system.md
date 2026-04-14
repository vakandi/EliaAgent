# Up for Role - Verification & Approval System

**Purpose**: Secure business context modifications with approval workflow

---

## System Overview

The "Up for Role" system prevents unauthorized changes to critical business context. Any new business addition requires explicit confirmation before being added to `business.md`.

---

## Workflow States

```
PENDING → REVIEW → APPROVED/REJECTED
```

### 1. **PENDING** State
Agent requests new business addition with:
- Business name & website
- Description (50-200 words)
- Business model & revenue
- Target markets
- Managing agents
- Expected impact

### 2. **REVIEW** State
System checks:
```json
{
  "validation": {
    "legal_status": "required",
    "revenue_status": "generating_or_planned",
    "operational_scope": "within_scope",
    "agent_assignment": "required",
    "conflict_check": "passed"
  }
}
```

### 3. **APPROVED** ✅ or **REJECTED** ❌
- **APPROVED**: Added to business.md with status 🟢
- **REJECTED**: Reason documented, can be resubmitted

---

## Agent Request Format

When requesting a new business, agents MUST provide:

```markdown
## Up for Role: [BUSINESS_NAME]

**Status**: PENDING  
**Requested By**: [AGENT_NAME]  
**Date**: YYYY-MM-DD  

### Business Details
- **Website**: https://...
- **Type**: B2B / B2C / Hybrid
- **Revenue Model**: [description]
- **Target Markets**: [regions/countries]

### Services/Products
- Item 1
- Item 2
- Item 3

### Managing Agents
- Development: Yes/No
- Marketing: Yes/No
- Sales: Yes/No
- [Others]

### Validation Checklist
- [ ] Legally registered
- [ ] Revenue-generating
- [ ] No conflicts
- [ ] Agents assigned
- [ ] Documentation complete

---

**Approval Decision**: [PENDING/APPROVED/REJECTED]  
**Reviewed By**: EliaIA System  
**Notes**: [if rejected]
```

---

## Current Pending Businesses

**Count**: 3-4 businesses awaiting documentation

### Template for Your Review

When you're ready, provide details for:
1. Business #5
2. Business #6  
3. Business #7
4. Business #8 (if exists)

---

## Protection Rules

✅ **ALLOWED**:
- View business context
- Request new business
- Update existing documentation (with approval)
- Add KPIs and metrics
- Monthly reviews

❌ **NOT ALLOWED**:
- Modify business.md without Up for Role
- Delete business context
- Bypass verification
- Unauthorized access

---

## Implementation Notes

This system integrates with:
- Git version control (tracks all changes)
- Agent logging (all requests recorded)
- Audit trail (monthly reviews)

**Never skip the Up for Role process.**
