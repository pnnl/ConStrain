# Product Manager Change Log

## Purpose

- Concise record of the workflow composer, validation, schema, Docker, and UI changes made in this workstream.
- Intended to help product management understand shipped scope and relative implementation effort by commit-sized change group.

## Commit Group Summary

| Commit Group | High-Level Change | Month/Year | Author | Effort (Rough LOC) |
| --- | --- | --- | --- | --- |
| 1 | Add workflow JSON reference for AI generation | Mar 2026 | Jerry | ~650-750 LOC |
| 2 | Inject workflow reference into LLM prompting | Mar 2026 | Jerry | ~120-180 LOC |
| 3 | Improve workflow composer UI for transparency and editing | Mar 2026 | Jerry | ~250-350 LOC |
| 4 | Fix Docker packaging for workflow reference availability | Mar 2026 | Jerry | ~5-10 LOC |
| 5 | Stabilize workflow validation around working directory errors | Mar 2026 | Jerry | ~60-100 LOC |
| 6 | Align workflow schema with documented rules | Mar 2026 | Jerry | ~300-450 LOC |

## Commit Group 1: Add Workflow JSON Reference for AI Generation

- Added a new workflow reference document to ground AI workflow generation in actual ConStrain behavior.
- Created a detailed markdown specification covering workflow structure, state types, payload handling, imports, control flow, and implementation constraints.
- Clarified that ConStrain API classes are pre-imported and should use shorthand method notation in generated workflows.
- Files touched:
  - `docs/Workflow_JSON_Structure_Reference.md`
- Effort:
  - ~650-750 LOC
  - Large documentation authoring effort with implementation-driven analysis.

## Commit Group 2: Inject Workflow Reference into LLM Prompting

- Updated workflow generation prompt assembly so the AI can use the full workflow reference as system-prompt guidance.
- Added support to load the markdown reference from disk and include it in workflow generation context.
- Added prompt guidance to discourage explicit `constrain.api` imports and favor shorthand method calls such as `DataProcessing.add_parameter`.
- Files touched:
  - `constrain/ai/workflow_composer.py`
  - `tests/test_ai_workflow_composer_prompt.py`
- Effort:
  - ~120-180 LOC
  - Prompt restructuring plus targeted test coverage for prompt content inclusion.

## Commit Group 3: Improve Workflow Composer UI for Transparency and Editing

- Added frontend running-state indicators so users can see when AI generation or workflow execution is in progress.
- Added downloadable markdown debug reports containing full LLM prompts and raw responses for workflow and case generation.
- Made generated verification-case JSON editable in the UI instead of read-only.
- Added backend support for storing and serving debug reports.
- Files touched:
  - `constrain/app/ai_workflow_ui.py`
  - `constrain/app/templates/ai_workflow_index.html`
  - `constrain/app/templates/ai_workflow_verification.html`
- Effort:
  - ~250-350 LOC
  - Cross-cut backend and frontend work, including state handling, report generation, and usability improvements.

## Commit Group 4: Fix Docker Packaging for Workflow Reference Availability

- Fixed container packaging so the workflow reference markdown is copied into runtime images.
- Resolved the issue where workflow generation inside Docker could not find the authoritative reference file.
- Updated multiple Docker images to ensure consistent behavior across API, UI, reporting, verification, and workflow services.
- Files touched:
  - `docker/Dockerfile.api-server`
  - `docker/Dockerfile.api-ui`
  - `docker/Dockerfile.reporting`
  - `docker/Dockerfile.verification`
  - `docker/Dockerfile.workflow`
- Effort:
  - ~5-10 LOC
  - Low code complexity, but important deployment and environment consistency fix.

## Commit Group 5: Stabilize Workflow Validation Around Working Directory Errors

- Fixed a runtime validation bug where non-Windows permission failures caused an `AttributeError` because the code assumed a Windows-only `winerror` field.
- Updated workflow validation so it checks workflow structure without trying to create or change into `working_dir` during validation.
- Prevented permission-related false failures during workflow generation and validation in containerized environments.
- Files touched:
  - `constrain/api/workflow.py`
  - `tests/test_workflow_validation.py`
- Effort:
  - ~60-100 LOC
  - Root-cause fix with regression coverage for cross-platform behavior.

## Commit Group 6: Align Workflow Schema with Documented Rules

- Updated the workflow JSON schema to support `working_dir`.
- Expanded schema support for embedded method calls inside parameters.
- Tightened state validation so `MethodCall` and `Choice` states match the documented structure more closely.
- Added schema support for logical choice expressions using `ALL`, `ANY`, and `NONE`.
- Preserved backward compatibility for legacy `AND` handling in runtime choice evaluation.
- Updated the workflow reference markdown to reflect the final `ALL` behavior and legacy compatibility note.
- Added schema and runtime regression tests for the new rules.
- Files touched:
  - `constrain/schema/workflow.schema.json`
  - `constrain/api/workflow.py`
  - `docs/Workflow_JSON_Structure_Reference.md`
  - `tests/schemas/test_schemas.py`
  - `tests/test_workflow_validation.py`
- Effort:
  - ~300-450 LOC
  - Required coordinated updates across documentation, schema, runtime behavior, and tests.

## Validation Summary

- Added targeted automated tests for prompt injection, schema updates, working directory validation, and logical choice behavior.
- Verified focused test runs passed after the changes.
- Current known non-blocking issue:
  - The workflow reference markdown still has markdown-lint formatting warnings, but these do not affect runtime behavior.

## Product Impact Summary

- Workflow generation is now better grounded by an authoritative reference instead of relying on sparse prompt guidance.
- Generated workflows are less likely to include invalid `constrain.api` imports or inconsistent method notation.
- The UI now gives users better operational visibility and debugging access.
- Docker behavior is consistent with local development for prompt grounding.
- Workflow validation is more robust in restricted environments.
- Schema support is now closer to actual supported workflow authoring patterns.
