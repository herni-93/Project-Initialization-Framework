# Arquitectura

> Guía para personas. Las instrucciones que sigue la IA están en `modules/` (en inglés).

## Visión general

El framework coordina módulos especializados que convierten una idea inicial en un proyecto
listo para ejecutar. No resuelve el problema del negocio: se asegura de que esté entendido y
especificado antes de que alguien lo resuelva.

Cada módulo tiene una sola responsabilidad y se comunica solo a través de delegaciones explícitas.

## Principios de arquitectura

- Responsabilidad única.
- Transiciones de estado explícitas.
- Ejecución determinista.
- Validación antes de avanzar.
- Sin supuestos ocultos.
- Composición modular.
- Independencia del modelo.

## Arquitectura general

```text
Pedido del usuario
      │
      ▼
Project Orchestrator ───────────── único dueño del estado
      │ delega
      ▼
Project Bootstrapper
      │                    │
      ▼                    ▼
Knowledge Connector   Discovery Engine
      │                    │
      └──── vuelven ───────┘
               ▼
Project Bootstrapper ── genera el PRD
               ▼
Project Orchestrator ── control de calidad, aprobación, handoff
```

## Módulos

| Módulo | Hace | No hace |
| --- | --- | --- |
| Project Orchestrator | Controla el flujo, cambia estados, valida resultados, pide aprobaciones, escribe el handoff | Entrevistar, analizar, escribir el PRD |
| Project Bootstrapper | Clasifica el pedido, mide claridad, delega, genera el PRD | Entrevistar, cambiar estados, planificar la ejecución |
| Discovery Engine | Entrevista adaptativa, resumen ejecutivo, validación con el usuario | Generar el PRD, leer bases de conocimiento, continuar el flujo |
| Knowledge Connector | Detecta y consulta (solo lectura) la base de conocimiento existente | Crear o modificar una base, decidir sin aprobación |

Detalle en [responsabilidades-de-modulos.md](responsabilidades-de-modulos.md).

## Modelo de comunicación

La delegación es jerárquica:

- El Orchestrator solo delega al Bootstrapper.
- El Bootstrapper delega al Knowledge Connector y al Discovery Engine.
- Cada módulo devuelve el control a quien lo invocó y nunca sigue el flujo por su cuenta.
- **Solo el Orchestrator cambia el estado.** Los demás módulos devuelven resultados y el
  Orchestrator decide si se avanza.

```text
Orchestrator
   └── Bootstrapper
         ├── Knowledge Connector
         └── Discovery Engine
```

## Coordinación de agentes

Con un solo agente de IA, el agente actúa de Orchestrator y "entra" en cada rol cargando el
archivo del módulo correspondiente solo cuando lo necesita. Si la herramienta permite subagentes,
el escaneo de la base de conocimiento se puede delegar a un subagente de solo lectura. La
entrevista nunca se delega en segundo plano, porque necesita hablar con el usuario.
Las reglas están en `AGENTS.md`.

## Extensibilidad

Se pueden agregar módulos nuevos sin tocar los existentes, siempre que:

- tengan una responsabilidad clara;
- se integren por la capa de orquestación;
- devuelvan el control al terminar.

## Objetivo de diseño

**Reducir la incertidumbre antes de que empiece la ejecución.**
