# T04 Prompt: PlatformConfig Component

```yaml
prompt_info:
  id: "prompt-0004"
  task_type: "code_generation"
  source_ref: "design-0002-component_platform_config"
  date: "2025-12-10"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

context:
  purpose: "Detect platform (GNU/BSD) and normalize command arguments"
  integration: "Platform domain component; used by BinaryExecutor for subprocess calls"
  knowledge_references: []
  constraints:
    - "Must handle both GNU (Linux) and BSD (macOS) tools"
    - "Lazy initialization on first use"

specification:
  description: "Create PlatformConfig class that locates binaries (sed/awk/diff), detects GNU vs BSD sed, and normalizes command arguments for platform-specific execution."
  
  requirements:
    functional:
      - "Locate sed, awk, diff binaries in PATH"
      - "Detect GNU sed via --version check"
      - "Normalize sed -i flag (GNU: -i.bak, BSD: -i .bak)"
      - "Cache binary paths"
      - "Raise BinaryNotFoundError if binaries missing"
    
    technical:
      language: "Python"
      version: "3.10+"
      standards:
        - "Thread-safe"
        - "Type hints"
        - "Professional docstrings"

design:
  architecture: "Class with lazy initialization and path caching"
  
  components:
    - name: "PlatformConfig"
      type: "class"
      logic:
        - "__init__: locate binaries, detect GNU sed"
        - "normalize_sed_args: adjust -i flag for platform"
        - "normalize_awk_args: return unchanged (no differences)"
        - "normalize_diff_args: return unchanged"
        - "_locate_binary: use shutil.which"
        - "_detect_gnu_sed: run sed --version, check for 'GNU sed'"
    
    - name: "BinaryNotFoundError"
      type: "class"
      logic:
        - "Custom exception for missing binaries"
  
  dependencies:
    internal: []
    external:
      - "shutil"
      - "subprocess"
      - "typing"

error_handling:
  exceptions:
    - exception: "BinaryNotFoundError"
      condition: "Required binary not in PATH"
      handling: "Raise at init time"
  logging:
    level: "DEBUG"
    format: "{timestamp} {level} PlatformConfig binary={name} path={path}"

deliverable:
  files:
    - path: "src/sed_awk_mcp/platform/config.py"
      content: "PlatformConfig class, BinaryNotFoundError exception, normalization logic"

success_criteria:
  - "Binaries located correctly"
  - "GNU detection works on both platforms"
  - "Sed -i normalization correct for GNU/BSD"
  - "Thread-safe implementation"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
