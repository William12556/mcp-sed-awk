Created: 2025 December 10

# Change: Implement BSD Sed Normalization

```yaml
change_info:
  id: "change-0001"
  title: "Implement BSD sed -i flag normalization"
  date: "2025-12-10"
  author: "Claude Desktop"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0001"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0001"
  description: "BSD sed -i normalization missing, breaking macOS/BSD compatibility"

scope:
  summary: "Add BSD branch to normalize_sed_args() method"
  affected_components:
    - name: "PlatformConfig"
      file_path: "src/sed_awk_mcp/platform/config.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0002-component_platform_config"
      sections: ["normalize_sed_args implementation"]

rational:
  problem_statement: "BSD sed requires -i with separate extension argument, GNU uses combined -i.ext"
  proposed_solution: "Implement BSD branch that inserts '.bak' as separate argument after -i"
  benefits:
    - "Enables BSD/macOS platform compatibility"
    - "Completes FR-09 platform detection requirement"

technical_details:
  current_behavior: "Only GNU normalization implemented, BSD returns unchanged args"
  proposed_behavior: |
    GNU: ['-i', 's/a/b/', 'file.txt'] → ['-i.bak', 's/a/b/', 'file.txt']
    BSD: ['-i', 's/a/b/', 'file.txt'] → ['-i', '.bak', 's/a/b/', 'file.txt']
  implementation_approach: |
    Modify normalize_sed_args():
    1. Find '-i' in args list
    2. If is_gnu_sed: append '.bak' to '-i' → '-i.bak'
    3. If NOT is_gnu_sed: insert '.bak' after '-i' index
    4. Return modified list
  code_changes:
    - component: "PlatformConfig"
      file: "src/sed_awk_mcp/platform/config.py"
      change_summary: "Add BSD normalization branch in normalize_sed_args()"
      functions_affected: ["normalize_sed_args"]

testing_requirements:
  test_approach: "Unit test verifies BSD normalization"
  test_cases:
    - scenario: "BSD sed with -i flag"
      expected_result: "['-i', '.bak', 's/a/b/', 'file.txt']"
  validation_criteria:
    - "TC-021 passes"
    - "All platform tests pass"

version_history:
  - version: "1.0"
    date: "2025-12-10"
    changes: ["Initial change document"]

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
