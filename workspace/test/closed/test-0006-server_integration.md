Created: 2025 December 10

# Test Document: Server Integration

```yaml
test_info:
  id: "test-0006"
  title: "FastMCP Server Integration Tests"
  date: "2025-12-10"
  status: "planned"
  type: "integration"
  priority: "critical"
  iteration: 1
  coupled_docs:
    prompt_ref: "prompt-0010"
    prompt_iteration: 1

source:
  test_target: "FastMCP server initialization and tool registration"
  requirement_refs:
    - "All functional requirements (FR-01 through FR-15)"

test_cases:
  - case_id: "TC-034"
    description: "Server initializes with sys.argv directories"
  - case_id: "TC-035"
    description: "Server falls back to ALLOWED_DIRECTORIES env var"
  - case_id: "TC-036"
    description: "Server defaults to current directory"
  - case_id: "TC-037"
    description: "All 5 tools registered"
  - case_id: "TC-038"
    description: "Component initialization fails fast on missing binaries"

test_execution_summary:
  total_cases: 5

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
