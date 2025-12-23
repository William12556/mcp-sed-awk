Created: 2025 December 10

# Test Document: Tools Domain Integration Tests

```yaml
test_info:
  id: "test-0005"
  title: "Tools Domain Integration Tests"
  date: "2025-12-10"
  status: "planned"
  type: "integration"
  priority: "critical"
  iteration: 1
  coupled_docs:
    prompt_ref: "prompt-0006,prompt-0007,prompt-0008,prompt-0009"
    prompt_iteration: 1

source:
  test_target: "sed_substitute, preview_sed, awk_transform, diff_files, list_allowed_directories"
  requirement_refs:
    - "FR-01: sed substitution"
    - "FR-02: awk transformation"
    - "FR-03: diff comparison"
    - "FR-04: preview changes"
    - "FR-05: list directories"
    - "FR-08: automatic backup"
    - "FR-11: error recovery"

test_cases:
  - case_id: "TC-026"
    description: "sed_substitute creates backup and edits file"
  - case_id: "TC-027"
    description: "sed_substitute rollback on failure"
  - case_id: "TC-028"
    description: "preview_sed generates diff without modifying file"
  - case_id: "TC-029"
    description: "awk_transform extracts fields correctly"
  - case_id: "TC-030"
    description: "diff_files generates unified diff"
  - case_id: "TC-031"
    description: "list_allowed_directories returns sorted list"
  - case_id: "TC-032"
    description: "File size >10MB rejected"
  - case_id: "TC-033"
    description: "Line range restriction works"

test_execution_summary:
  total_cases: 8

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
