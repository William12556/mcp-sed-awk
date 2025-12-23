Created: 2025 December 10

# Issue: BSD Sed Normalization Not Implemented

```yaml
issue_info:
  id: "issue-0001"
  title: "BSD sed -i normalization missing implementation"
  date: "2025-12-10"
  reporter: "Claude Desktop"
  status: "open"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "test_result"
  test_ref: "test-0004"
  description: "TC-021 failure: BSD sed normalization returns incorrect args"

affected_scope:
  components:
    - name: "PlatformConfig"
      file_path: "src/sed_awk_mcp/platform/config.py"
  designs:
    - design_ref: "design-0002-component_platform_config"
  version: "0.1.0"

reproduction:
  prerequisites: "PlatformConfig instantiated with is_gnu_sed = False"
  steps:
    - "Create PlatformConfig instance"
    - "Set config.is_gnu_sed = False"
    - "Call config.normalize_sed_args(['-i', 's/a/b/', 'file.txt'])"
  frequency: "always"
  reproducibility_conditions: "When is_gnu_sed = False"
  error_output: |
    AssertionError: assert ['-i', 's/a/b/', 'file.txt'] == ['-i', '.bak', 's/a/b/', 'file.txt']
    At index 1 diff: 's/a/b/' != '.bak'

behavior:
  expected: "BSD mode should insert '.bak' after '-i': ['-i', '.bak', 's/a/b/', 'file.txt']"
  actual: "Returns original args unchanged: ['-i', 's/a/b/', 'file.txt']"
  impact: "BSD sed will fail or behave incorrectly without proper -i syntax"
  workaround: "None - breaks BSD platform compatibility"

environment:
  python_version: "3.11.14"
  os: "macOS (darwin)"
  domain: "domain_1"

analysis:
  root_cause: |
    PlatformConfig.normalize_sed_args() method exists but only implements
    GNU sed normalization branch. BSD sed branch missing or incomplete.
    
    Expected logic:
    - GNU sed: '-i' → '-i.bak'
    - BSD sed: '-i' → '-i', '.bak' (separate arguments)
  technical_notes: |
    Design specification (design-0002-component_platform_config) requires:
    "normalize_sed_args() adapts -i flag based on detected sed variant"
    
    Current implementation likely has empty or placeholder BSD branch.

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-10"
  approach: |
    Implement BSD sed -i normalization:
    1. Detect '-i' in args
    2. If is_gnu_sed: append '.bak' to '-i' → '-i.bak'
    3. If NOT is_gnu_sed: insert '.bak' after '-i' as separate arg
    4. Return modified args list
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verification_steps:
    - "Run TC-021: test_sed_normalization_bsd"
    - "Verify ['-i', '.bak', 's/a/b/', 'file.txt'] returned"
    - "Run full platform test suite"
  verification_results: ""

prevention:
  preventive_measures: "Add explicit test cases for both GNU and BSD variants in all platform-dependent logic"
  process_improvements: "Code generation prompts should include platform compatibility verification requirements"

traceability:
  design_refs:
    - "design-0002-component_platform_config"
  change_refs: []
  test_refs:
    - "test-0004"

notes: |
  FR-09 requires platform detection and compatibility. This defect breaks
  BSD platform support, preventing sed operations on macOS/BSD systems.

version_history:
  - version: "1.0"
    date: "2025-12-10"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from test failure"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
