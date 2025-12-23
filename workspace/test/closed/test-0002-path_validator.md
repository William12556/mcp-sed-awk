Created: 2025 December 10

# Test Document: PathValidator Component

```yaml
test_info:
  id: "test-0002"
  title: "PathValidator Unit Tests"
  date: "2025-12-10"
  status: "planned"
  type: "unit"
  priority: "critical"
  iteration: 1
  coupled_docs:
    prompt_ref: "prompt-0002"
    prompt_iteration: 1

source:
  test_target: "PathValidator class"
  requirement_refs:
    - "FR-06: Directory whitelist enforcement"
    - "NFR-08: Path traversal prevention"

test_cases:
  - case_id: "TC-011"
    description: "Valid path in allowed directory passes"
    category: "positive"
    inputs:
      - parameter: "path"
        value: "/tmp/test/file.txt"
    expected_outputs:
      - field: "return"
        expected_value: "Path('/tmp/test/file.txt')"
    
  - case_id: "TC-012"
    description: "Path traversal with ../ blocked"
    category: "negative"
    inputs:
      - parameter: "path"
        value: "/tmp/test/../../etc/passwd"
    expected_outputs:
      - field: "exception"
        expected_value: "SecurityError"
    
  - case_id: "TC-013"
    description: "Symlink to forbidden location blocked"
    category: "negative"
    inputs:
      - parameter: "path"
        value: "/tmp/test/link_to_etc"
    expected_outputs:
      - field: "exception"
        expected_value: "SecurityError"
    
  - case_id: "TC-014"
    description: "Empty whitelist raises ValueError at init"
    category: "negative"
    inputs:
      - parameter: "allowed_dirs"
        value: "[]"
    expected_outputs:
      - field: "exception"
        expected_value: "ValueError"
    
  - case_id: "TC-015"
    description: "Invalid directory in whitelist raises ValueError"
    category: "negative"
    inputs:
      - parameter: "allowed_dirs"
        value: "['/nonexistent']"
    expected_outputs:
      - field: "exception"
        expected_value: "ValueError"

test_execution_summary:
  total_cases: 5

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
