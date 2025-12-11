Created: 2025 December 10

# Test Document: Platform Domain (PlatformConfig + BinaryExecutor)

```yaml
test_info:
  id: "test-0004"
  title: "Platform Domain Unit Tests"
  date: "2025-12-10"
  status: "planned"
  type: "unit"
  priority: "high"
  iteration: 1
  coupled_docs:
    prompt_ref: "prompt-0004,prompt-0005"
    prompt_iteration: 1

source:
  test_target: "PlatformConfig, BinaryExecutor"
  requirement_refs:
    - "FR-09: Platform detection"
    - "FR-10: Subprocess timeout"
    - "NFR-02: 30s timeout"
    - "NFR-11: Platform portability"

test_cases:
  - case_id: "TC-019"
    description: "Binaries located in PATH"
  - case_id: "TC-020"
    description: "GNU sed detected correctly"
  - case_id: "TC-021"
    description: "Sed -i normalization (GNU vs BSD)"
  - case_id: "TC-022"
    description: "Missing binary raises BinaryNotFoundError"
  - case_id: "TC-023"
    description: "Subprocess executes with shell=False"
  - case_id: "TC-024"
    description: "30s timeout enforced"
  - case_id: "TC-025"
    description: "Resource limits set on Linux"

test_execution_summary:
  total_cases: 7

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
