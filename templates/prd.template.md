---
id: {{id_json}}
name: {{name_json}}
document: prd
version: {{prd_version}}
status: draft
project_type: "{{project_type}}"
created: "{{created}}"
updated: "{{updated}}"
clarity_score: {{clarity}}
recommended_resources: {{resources_inline}}
generated_by: "project-initialization-framework {{framework_version}}"
---

# PRD - {{name}}

> Single source of truth for this project. Every value comes from the validated
> executive summary. Nothing here was assumed: unknowns are listed under Open Questions.

## 1. Objective

{{objective}}

## 2. Problem

{{problem}}

## 3. Context

{{context}}

## 4. Expected Result

{{expected_result}}

## 5. Deliverables

{{deliverables}}

## 6. Success Criteria

{{success_criteria}}

## 7. Constraints

{{constraints}}

## 8. Risks

{{risks}}

## 9. Dependencies

{{dependencies}}

## 10. Knowledge & Resources

{{knowledge_section}}

{{resources_table}}

## 11. Open Questions

{{open_questions}}

## 12. Initialization Metrics

| Metric | Value |
| --- | --- |
| Clarity score (initial -> final) | {{clarity_initial}} -> {{clarity}} / 100 |
| Uncertainty level | {{uncertainty_level}} |
| Questions answered | {{questions_answered}} |
| Discovery skipped | {{discovery_skipped}} |
| Summary rejections | {{summary_rejections}} |
| PRD rejections | {{prd_rejections}} |

## 13. Handoff

Initialization ends when this PRD is approved. The next execution layer
(planning, architecture, implementation) receives this PRD and `handoff.json`.
Any change to objective, deliverables or success criteria after approval must
go back through discovery and validation.
