# Software Project Workflow

## Initial Request

> "I want to build a SaaS platform for freelance designers."

---

# Framework Initialization

The Project Orchestrator receives the request and delegates project initialization to the Project Bootstrapper.

The Bootstrapper evaluates the available information and determines that the project definition is incomplete.

Discovery is required before a specification can be generated.

---

# Adaptive Discovery

The Project Bootstrapper delegates control to the Discovery Engine.

Rather than using a fixed questionnaire, the Discovery Engine conducts an adaptive interview, asking only the questions required to reduce uncertainty.

Example questions may include:

- Who are the target users?
- What problem does the platform solve?
- What are the core features?
- What is considered the MVP?
- Are there technical or business constraints?
- How will success be measured?

The interview stops automatically once sufficient information has been collected.

---

# Validation

The Discovery Engine generates an executive summary describing the project.

The summary is presented to the user for validation.

If changes are requested, discovery continues only where clarification is needed.

Once approved, control returns to the Project Bootstrapper.

---

# PRD Generation

Using the validated project definition, the Project Bootstrapper generates a structured Product Requirements Document (PRD).

The PRD becomes the project's initial specification and source of truth.

Control is then returned to the Project Orchestrator.

---

# Result

✅ Project successfully initialized

✅ Validated project definition

✅ Structured PRD generated

✅ Project ready for execution