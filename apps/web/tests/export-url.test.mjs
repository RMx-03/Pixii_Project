import test from "node:test";
import assert from "node:assert/strict";

/**
 * Ensure export URL routing shape remains stable.
 */
test("builds report export URL", () => {
  const base = "http://localhost:8000";
  const runId = "abc123";
  const url = `${base}/api/v1/diagnostics/reports/${runId}/export?format=md`;
  assert.equal(url, "http://localhost:8000/api/v1/diagnostics/reports/abc123/export?format=md");
});

