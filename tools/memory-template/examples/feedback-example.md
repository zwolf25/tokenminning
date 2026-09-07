---
name: feedback-no-mock-db-in-integration-tests
description: "Integration tests must hit a real database, not mocks"
metadata:
  node_type: memory
  type: feedback
---

Integration tests for the billing service must run against a real (test) database instance, never a mocked DB layer.

**Why:** a prior incident shipped a migration where mocked tests passed but the real schema change broke a foreign-key constraint in production. The mock diverged from real DB behavior in a way nobody caught until after deploy.

**How to apply:** when writing or reviewing integration tests for anything touching persistence, flag a mocked database as a blocker, not a style preference. Unit tests for pure logic can still mock freely — this rule is scoped to integration tests specifically.
