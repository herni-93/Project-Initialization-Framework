---
id: "plataforma-para-disenadores-freelance-2026-11-02"
name: "Plataforma para diseñadores freelance"
document: prd
version: 1
status: approved
project_type: "software"
created: "2026-11-02T14:57:58+00:00"
updated: "2026-11-02T14:57:59+00:00"
clarity_score: 90
recommended_resources: ["SYSTEM.md", "saas-mvp-scoping", "launch-checklist", "Freelance designers", "freelance-designers-interviews", "product-manager"]
generated_by: "project-initialization-framework 2.1.0"
---

# PRD - Plataforma para diseñadores freelance

> Single source of truth for this project. Every value comes from the validated
> executive summary. Nothing here was assumed: unknowns are listed under Open Questions.

## 1. Objective

Quiero construir una plataforma SaaS para diseñadores freelance

## 2. Problem

Los diseñadores freelance usan entre 4 y 6 herramientas para gestionar clientes y facturas

## 3. Context

_Open question - not answered yet._

## 4. Expected Result

Aplicación web desplegada y usada por un grupo de diseñadores beta

## 5. Deliverables

MVP web con portfolio, facturación y portal de clientes

## 6. Success Criteria

- Que los usuarios la usen
- 100 diseñadores pagando la suscripción dentro de los 6 meses del lanzamiento

## 7. Constraints

- Presupuesto máximo de 5000 USD
- lanzamiento antes de marzo 2027

## 8. Risks

_Open question - not answered yet._

## 9. Dependencies

None identified.

## 10. Knowledge & Resources

Connected sources (read-only):
- `examples/sample-knowledge-base` (markdown)
- `examples/sample-knowledge-base/graph.json` (json-graph)

Relevant notes found:
- **Freelance designers interviews** (`examples/sample-knowledge-base/knowledge/freelance-designers-interviews.md`): Notes from 12 interviews with freelance designers: invoicing and client
- **SaaS MVP Scoping** (`examples/sample-knowledge-base/skills/saas-mvp-scoping/SKILL.md`): Scope a SaaS MVP for freelancers - core features, invoicing, client portal.
- **saas-mvp-scoping** (`examples/sample-knowledge-base/graph.json#n2`): Skill to scope a SaaS MVP for freelancers. | related: Freelance designers
- **Freelance designers** (`examples/sample-knowledge-base/graph.json#n1`): Segment: freelance designers that manage clients and invoicing alone. | related: Invoicing pain, saas-mvp-scoping
- **Product Manager** (`examples/sample-knowledge-base/system-prompts/product-manager.md`): You act as a pragmatic product manager for SaaS products...

| Resource | Type | Reason | Priority | Status |
| --- | --- | --- | --- | --- |
| SYSTEM.md | system_prompt | global working instructions of the user | high | approved |
| saas-mvp-scoping | skill | matches: saas, freelance, portal | high | approved |
| launch-checklist | workflow | matches: freelance, beta | medium | approved |
| Freelance designers | knowledge | matches: freelance | low | approved |
| freelance-designers-interviews | knowledge | matches: freelance | low | approved |
| product-manager | system_prompt | matches: saas | low | approved |

## 11. Open Questions

- **Context**: missing
- **Risks**: missing

## 12. Initialization Metrics

| Metric | Value |
| --- | --- |
| Clarity score (initial -> final) | 20 -> 90 / 100 |
| Uncertainty level | low |
| Questions answered | 6 |
| Discovery skipped | no |
| Summary rejections | 1 |
| PRD rejections | 0 |

## 13. Handoff

Initialization ends when this PRD is approved. The next execution layer
(planning, architecture, implementation) receives this PRD and `handoff.json`.
Any change to objective, deliverables or success criteria after approval must
go back through discovery and validation.
