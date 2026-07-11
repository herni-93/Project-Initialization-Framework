# State Machine

## Overview

The Project Initialization Framework follows a deterministic state machine managed exclusively by the Project Orchestrator.

Each project progresses through a predefined sequence of states.

State transitions occur only after the current stage has completed successfully and all validation requirements have been satisfied.

Components never modify the project state directly.

Their responsibility is to complete their assigned work and return control to the Project Orchestrator.

---

# State Diagram

```text
waiting
    │
    ▼
bootstrap
    │
    ▼
discovery
    │
    ▼
validation
    │
    ▼
prd_generation
    │
    ▼
completed
```

The state machine defines the only valid progression through the project initialization lifecycle.

---

# State Definitions

## waiting

The framework is idle and waiting for a new project request.

**Owner:** Project Orchestrator

---

## bootstrap

The Project Bootstrapper initializes the project and evaluates whether additional discovery is required.

If sufficient information already exists, the workflow may continue directly to PRD generation.

**Owner:** Project Orchestrator

---

## discovery

The Discovery Engine gathers missing information through an adaptive interview.

The objective is to reduce uncertainty without asking unnecessary questions.

**Owner:** Project Orchestrator

---

## validation

The discovered project definition is presented to the user.

The workflow cannot continue until the project summary has been explicitly approved.

If modifications are required, the workflow returns to the Discovery state.

**Owner:** Project Orchestrator

---

## prd_generation

The Project Bootstrapper generates the Product Requirements Document (PRD) using the validated project definition.

The generated PRD becomes the project's initial specification.

**Owner:** Project Orchestrator

---

## completed

Project initialization has finished successfully.

The framework has fulfilled its responsibility and the project is ready to be handed over to the next orchestration or execution layer.

**Owner:** Project Orchestrator

---

# State Transitions

The framework allows only the following transitions:

```text
waiting
    │
    ▼
bootstrap
    │
    ├──────────────┐
    ▼              │
discovery          │
    │              │
    ▼              │
validation─────────┘
    │
    ▼
prd_generation
    │
    ▼
completed
```

If validation fails, the workflow returns to the **Discovery** state until the project definition has been corrected and approved.

No other transitions are permitted.

---

# Transition Rules

- States must be completed sequentially.
- States cannot be skipped.
- Every transition requires successful completion of the previous state.
- Validation is mandatory before PRD generation.
- Only the Project Orchestrator can change the current project state.

---

# Error Handling

If a component cannot complete its responsibility:

- The current state remains unchanged.
- The workflow is paused.
- The issue must be resolved before the state transition can occur.

The framework always resumes from the last valid state rather than restarting the entire initialization process.

---

# Design Goal

The state machine guarantees that every project follows the same predictable initialization lifecycle.

By centralizing state management within the Project Orchestrator, the framework ensures that execution only begins after the project has been fully understood, validated, and documented.