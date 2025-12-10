Created: 2025 December 10

# Traceability Matrix - mcp-sed-awk

## Table of Contents

1. [Functional Requirements](<#1.0 functional requirements>)
2. [Non-Functional Requirements](<#2.0 non-functional requirements>)
3. [Component Mapping](<#3.0 component mapping>)
4. [Design Document Cross-Reference](<#4.0 design document cross-reference>)
5. [Test Coverage](<#5.0 test coverage>)
6. [Bidirectional Navigation](<#6.0 bidirectional navigation>)
7. [Version History](<#version history>)

---

## 1.0 Functional Requirements

| ID | Requirement | Design | Code | Test | Status |
|----|-------------|--------|------|------|--------|
| FR-01 | sed pattern substitution with regex support | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.5 tool: sed_substitute>), [design-0003-sed](<../design/design-0003-component_tools_sed.md#2.0 sed_substitute tool>) | TBD | TBD | Approved |
| FR-02 | awk field extraction and transformation | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.6 tool: awk_transform>), [design-0003-awk](<../design/design-0003-component_tools_awk.md#2.0 awk_transform tool>) | TBD | TBD | Approved |
| FR-03 | diff file comparison with unified output | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.7 tool: diff_files>), [design-0003-diff](<../design/design-0003-component_tools_diff.md#2.0 diff_files tool>) | TBD | TBD | Approved |
| FR-04 | Preview sed changes before application | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.8 tool: preview_sed>), [design-0003-sed](<../design/design-0003-component_tools_sed.md#3.0 preview_sed tool>) | TBD | TBD | Approved |
| FR-05 | List accessible directories | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.9 tool: list_allowed_directories>), [design-0003-list](<../design/design-0003-component_tools_list.md#2.0 list_allowed_directories tool>) | TBD | TBD | Approved |
| FR-06 | Directory whitelist enforcement | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.3 pathvalidator>), [design-0001-path](<../design/design-0001-component_security_path.md>) | TBD | TBD | Approved |
| FR-07 | Input validation for patterns and programs | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#6.2 securityvalidator>), [design-0001-validator](<../design/design-0001-component_security_validator.md>) | TBD | TBD | Approved |
| FR-08 | Automatic backup creation for sed operations | [design-0003-sed](<../design/design-0003-component_tools_sed.md#2.2 implementation logic>) | TBD | TBD | Approved |
| FR-09 | Platform detection (GNU vs BSD tools) | [design-0002-config](<../design/design-0002-component_platform_config.md>) | TBD | TBD | Approved |
| FR-10 | Subprocess timeout enforcement | [design-0002-executor](<../design/design-0002-component_platform_executor.md#4.0 processing logic>) | TBD | TBD | Approved |
| FR-11 | Error recovery with backup restoration | [design-0003-sed](<../design/design-0003-component_tools_sed.md#2.2 implementation logic>) | TBD | TBD | Approved |
| FR-12 | Audit logging for security events | [design-0001-audit](<../design/design-0001-component_security_audit.md>) | TBD | TBD | Approved |
| FR-13 | Line range restriction for sed operations | [design-0003-sed](<../design/design-0003-component_tools_sed.md#2.1 function signature>) | TBD | TBD | Approved |
| FR-14 | Custom field separator for awk | [design-0003-awk](<../design/design-0003-component_tools_awk.md#2.1 function signature>) | TBD | TBD | Approved |
| FR-15 | Configurable unified diff context lines | [design-0003-diff](<../design/design-0003-component_tools_diff.md#2.1 function signature>) | TBD | TBD | Approved |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Non-Functional Requirements

| ID | Requirement | Target | Design | Code | Test | Status |
|----|-------------|--------|--------|------|------|--------|
| NFR-01 | Operation latency | < 5s typical | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#10.1 performance>) | TBD | TBD | Approved |
| NFR-02 | Maximum operation timeout | 30s | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.3 performance targets>) | TBD | TBD | Approved |
| NFR-03 | File size limit | 10 MB | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.3 performance targets>) | TBD | TBD | Approved |
| NFR-04 | Pattern length limit | 1000 chars | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.3 performance targets>) | TBD | TBD | Approved |
| NFR-05 | AWK program length limit | 2000 chars | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.3 performance targets>) | TBD | TBD | Approved |
| NFR-06 | Memory per operation (Linux) | 100 MB max | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.3 performance targets>) | TBD | TBD | Approved |
| NFR-07 | CPU time per operation (Linux) | 30s max | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.3 performance targets>) | TBD | TBD | Approved |
| NFR-08 | Path traversal prevention | TOCTOU-resistant | [design-0001-path](<../design/design-0001-component_security_path.md#4.2 path validation>) | TBD | TBD | Approved |
| NFR-09 | Command injection prevention | No shell=True | [design-0002-executor](<../design/design-0002-component_platform_executor.md#4.1 execution flow>) | TBD | TBD | Approved |
| NFR-10 | ReDoS protection | Complexity limits | [design-0001-validator](<../design/design-0001-component_security_validator.md#4.0 processing logic>) | TBD | TBD | Approved |
| NFR-11 | Platform portability | Linux + macOS | [design-0002-domain](<../design/design-0002-domain_platform.md>) | TBD | TBD | Approved |
| NFR-12 | Thread safety | All components | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#4.2 implementation>) | TBD | TBD | Approved |
| NFR-13 | Code coverage | 80% minimum | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#10.4 maintainability>) | TBD | TBD | Approved |
| NFR-14 | Error recovery | Automatic rollback | [design-0000](<../design/design-0000-master_sed-awk-mcp.md#10.3 reliability>) | TBD | TBD | Approved |
| NFR-15 | Audit trail completeness | All security events | [design-0001-audit](<../design/design-0001-component_security_audit.md>) | TBD | TBD | Approved |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Component Mapping

| Component | Requirements | Design | Source | Test |
|-----------|--------------|--------|--------|------|
| SecurityValidator | FR-07, NFR-10 | [design-0001-validator](<../design/design-0001-component_security_validator.md>) | TBD | TBD |
| PathValidator | FR-06, NFR-08 | [design-0001-path](<../design/design-0001-component_security_path.md>) | TBD | TBD |
| AuditLogger | FR-12, NFR-15 | [design-0001-audit](<../design/design-0001-component_security_audit.md>) | TBD | TBD |
| PlatformConfig | FR-09, NFR-11 | [design-0002-config](<../design/design-0002-component_platform_config.md>) | TBD | TBD |
| BinaryExecutor | FR-10, NFR-02, NFR-06, NFR-07, NFR-09 | [design-0002-executor](<../design/design-0002-component_platform_executor.md>) | TBD | TBD |
| sed_substitute | FR-01, FR-08, FR-11, FR-13 | [design-0003-sed](<../design/design-0003-component_tools_sed.md>) | TBD | TBD |
| preview_sed | FR-04 | [design-0003-sed](<../design/design-0003-component_tools_sed.md>) | TBD | TBD |
| awk_transform | FR-02, FR-14 | [design-0003-awk](<../design/design-0003-component_tools_awk.md>) | TBD | TBD |
| diff_files | FR-03, FR-15 | [design-0003-diff](<../design/design-0003-component_tools_diff.md>) | TBD | TBD |
| list_allowed_directories | FR-05 | [design-0003-list](<../design/design-0003-component_tools_list.md>) | TBD | TBD |
| ServerConfig | NFR-11, NFR-12 | [design-0004-config](<../design/design-0004-component_server_config.md>) | TBD | TBD |
| ErrorHandler | NFR-14 | [design-0004-error](<../design/design-0004-component_server_error.md>) | TBD | TBD |
| FastMCP Server | All FR, All NFR | [design-0004-main](<../design/design-0004-component_server_main.md>) | TBD | TBD |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Design Document Cross-Reference

| Design Doc | Requirements | Code | Tests |
|------------|--------------|------|-------|
| [design-0000-master](<../design/design-0000-master_sed-awk-mcp.md>) | All FR, All NFR | TBD | TBD |
| [design-0001-domain-security](<../design/design-0001-domain_security.md>) | FR-06, FR-07, FR-12, NFR-08, NFR-10, NFR-15 | TBD | TBD |
| [design-0001-validator](<../design/design-0001-component_security_validator.md>) | FR-07, NFR-04, NFR-05, NFR-10 | TBD | TBD |
| [design-0001-path](<../design/design-0001-component_security_path.md>) | FR-06, NFR-08 | TBD | TBD |
| [design-0001-audit](<../design/design-0001-component_security_audit.md>) | FR-12, NFR-15 | TBD | TBD |
| [design-0002-domain-platform](<../design/design-0002-domain_platform.md>) | FR-09, FR-10, NFR-02, NFR-06, NFR-07, NFR-09, NFR-11 | TBD | TBD |
| [design-0002-config](<../design/design-0002-component_platform_config.md>) | FR-09, NFR-11 | TBD | TBD |
| [design-0002-executor](<../design/design-0002-component_platform_executor.md>) | FR-10, NFR-02, NFR-06, NFR-07, NFR-09 | TBD | TBD |
| [design-0003-domain-tools](<../design/design-0003-domain_tools.md>) | FR-01 through FR-05, FR-08, FR-11, FR-13, FR-14, FR-15, NFR-01, NFR-03 | TBD | TBD |
| [design-0003-sed](<../design/design-0003-component_tools_sed.md>) | FR-01, FR-04, FR-08, FR-11, FR-13 | TBD | TBD |
| [design-0003-awk](<../design/design-0003-component_tools_awk.md>) | FR-02, FR-14 | TBD | TBD |
| [design-0003-diff](<../design/design-0003-component_tools_diff.md>) | FR-03, FR-15 | TBD | TBD |
| [design-0003-list](<../design/design-0003-component_tools_list.md>) | FR-05 | TBD | TBD |
| [design-0004-domain-server](<../design/design-0004-domain_server.md>) | All FR, NFR-11, NFR-12, NFR-14 | TBD | TBD |
| [design-0004-config](<../design/design-0004-component_server_config.md>) | FR-06, NFR-11, NFR-12 | TBD | TBD |
| [design-0004-error](<../design/design-0004-component_server_error.md>) | FR-11, NFR-14 | TBD | TBD |
| [design-0004-main](<../design/design-0004-component_server_main.md>) | All FR, All NFR | TBD | TBD |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Test Coverage

| Test File | Requirements Verified | Code Coverage |
|-----------|----------------------|---------------|
| test_security_validator.py | FR-07, NFR-04, NFR-05, NFR-10 | TBD |
| test_path_validator.py | FR-06, NFR-08 | TBD |
| test_audit_logger.py | FR-12, NFR-15 | TBD |
| test_platform_config.py | FR-09, NFR-11 | TBD |
| test_binary_executor.py | FR-10, NFR-02, NFR-06, NFR-07, NFR-09 | TBD |
| test_sed_tool.py | FR-01, FR-04, FR-08, FR-11, FR-13 | TBD |
| test_awk_tool.py | FR-02, FR-14 | TBD |
| test_diff_tool.py | FR-03, FR-15 | TBD |
| test_list_tool.py | FR-05 | TBD |
| test_server_config.py | FR-06, NFR-11, NFR-12 | TBD |
| test_error_handler.py | FR-11, NFR-14 | TBD |
| test_server_main.py | Integration: All FR | TBD |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Bidirectional Navigation

### 6.1 Forward Traceability

**Requirement → Design → Code → Test**

Example navigation path:
- FR-01 (sed substitution) 
  - → design-0000#6.5, design-0003-sed#2.0
  - → src/sed_awk_mcp/tools/sed_tool.py
  - → tests/sed_awk_mcp/test_sed_tool.py

### 6.2 Backward Traceability

**Test → Code → Design → Requirement**

Example navigation path:
- tests/sed_awk_mcp/test_sed_tool.py
  - → src/sed_awk_mcp/tools/sed_tool.py
  - → design-0003-sed#2.0, design-0000#6.5
  - → FR-01, FR-04, FR-08, FR-11, FR-13

### 6.3 Orphan Detection

Components without design traceability: None (all components designed)

Requirements without implementation: TBD (pending code generation)

Tests without requirements: None (design specifies test requirements)

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | William Watson | Initial traceability matrix with complete FR/NFR mapping |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
