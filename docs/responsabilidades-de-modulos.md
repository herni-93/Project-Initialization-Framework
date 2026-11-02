# Responsabilidades de los módulos

> Guía para personas. Cada módulo tiene su instrucción completa (en inglés) en `modules/`.

## Principio

Un módulo hace una sola cosa. Si hace falta otra responsabilidad, se delega al módulo que
corresponde. Así el framework es predecible y fácil de extender.

---

## Project Orchestrator

**Responsabilidad:** ser dueño del ciclo de vida completo. Es el único punto de entrada.

| | |
| --- | --- |
| Invocado por | Usuario (u otro orquestador superior) |
| Delega a | Project Bootstrapper |
| Devuelve el control a | La siguiente capa de ejecución |
| Es dueño de | Estado, transiciones, guardas, control de calidad del PRD, aprobaciones, manejo de errores, handoff |
| No hace | Entrevistas, análisis, PRD, selección de recursos |

---

## Project Bootstrapper

**Responsabilidad:** convertir el pedido en una definición estructurada y generar el PRD.

| | |
| --- | --- |
| Invocado por | Project Orchestrator |
| Delega a | Knowledge Connector, Discovery Engine |
| Devuelve el control a | Project Orchestrator |
| Es dueño de | Clasificación del proyecto, medición inicial de claridad, generación del PRD |
| No hace | Entrevistas, validación, cambios de estado, planes de ejecución |

---

## Discovery Engine

**Responsabilidad:** reducir la incertidumbre antes de cualquier plan.

| | |
| --- | --- |
| Invocado por | Project Bootstrapper |
| Delega a | Nadie |
| Devuelve el control a | Project Bootstrapper |
| Es dueño de | Entrevista adaptativa, puntaje de incertidumbre, resumen ejecutivo, validación con el usuario |
| No hace | PRD, lectura de bases de conocimiento, cambios de estado, continuar el flujo |

---

## Knowledge Connector

**Responsabilidad:** conectarse, en modo lectura, a la base de conocimiento que el usuario ya tiene.

| | |
| --- | --- |
| Invocado por | Project Bootstrapper |
| Delega a | Nadie |
| Devuelve el control a | Project Bootstrapper |
| Es dueño de | Detección de fuentes, pregunta de consentimiento, inventario, búsqueda, propuesta de recursos |
| No hace | Crear, modificar o copiar una base; tomar valores como ciertos sin aprobación |

---

## Límites

```text
Usuario
 │
 ▼
Project Orchestrator ─── coordina y cambia el estado
 │
 ▼
Project Bootstrapper ─── inicializa y especifica
 ├── Knowledge Connector ─── consulta lo que ya existe
 └── Discovery Engine ────── descubre y valida
```

## Reglas de delegación

- Las responsabilidades no se duplican.
- Los módulos se comunican solo por delegación explícita, con quien los invocó o con quien delegan.
- Solo el Orchestrator controla el avance del flujo.
- Toda tarea delegada devuelve el control antes de que el flujo continúe.
