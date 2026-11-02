# Máquina de estados

> Guía para personas. La implementación está en `pif/states.py` y la instrucción para la IA en
> `modules/project-orchestrator.md`.

## Visión general

Cada inicialización pasa por una secuencia fija de estados. **Solo el Project Orchestrator
cambia el estado**; los demás módulos hacen su trabajo y devuelven el resultado.

## Estados

| Estado | Significado | Quién trabaja |
| --- | --- | --- |
| `waiting` | No hay inicialización en curso | - |
| `bootstrap` | Clasificación, base de conocimiento y medición de claridad | Bootstrapper (+ Knowledge Connector) |
| `discovery` | Entrevista adaptativa | Discovery Engine |
| `validation` | Resumen ejecutivo esperando aprobación | Discovery Engine + usuario |
| `prd_generation` | Generación del PRD | Bootstrapper |
| `prd_review` | PRD esperando aprobación | Orchestrator + usuario |
| `completed` | PRD aprobado y handoff escrito | - |
| `cancelled` | Cancelado por el usuario | - |
| `error` | Un módulo falló; el flujo está en pausa | - |

## Transiciones permitidas

```text
waiting ──► bootstrap ──► discovery ──► validation ──► prd_generation ──► prd_review ──► completed
                │                          ▲   │                               │
                └──────────────────────────┘   │                               │
                 (información suficiente)      ▼                               │
                                          discovery ◄──────────────────────────┘
                                       (cambios pedidos por el usuario)

cualquier estado activo ──► cancelled
cualquier estado activo ──► error ──► último estado válido (reanudar)
```

| Desde | Hacia | Condición |
| --- | --- | --- |
| `waiting` | `bootstrap` | Llegó un pedido |
| `bootstrap` | `discovery` | Claridad insuficiente |
| `bootstrap` | `validation` | Claridad suficiente (se saltea el descubrimiento) |
| `discovery` | `validation` | Claridad suficiente, 12 preguntas, o el usuario pide terminar |
| `validation` | `discovery` | El usuario rechaza o cambia el resumen |
| `validation` | `prd_generation` | Aprobado y con campos críticos completos |
| `prd_generation` | `prd_review` | PRD generado y aprobado por el control de calidad |
| `prd_review` | `discovery` | El usuario pide cambios |
| `prd_review` | `completed` | El usuario aprueba y el checklist final pasa |

Ninguna otra transición está permitida. La implementación de referencia rechaza cualquier otra.

## Por qué el descubrimiento es opcional y la validación no

Si el pedido ya trae toda la información, preguntar de nuevo es un desperdicio. Pero el
usuario siempre tiene que confirmar que lo entendido es correcto. Por eso `bootstrap` puede
ir directo a `validation`, pero nunca directo a `prd_generation`.

## Manejo de errores

Si un módulo no puede terminar:

- el estado pasa a `error` y se guarda el último estado válido;
- se informa qué falló;
- una vez corregido, `pif resume` vuelve al último estado válido.

Nunca se reinicia todo si no es necesario.

## Persistencia

El estado se guarda en `.pif/state.json` (formato en `templates/project-state.schema.json`)
y cada transición queda registrada en `.pif/events.jsonl`.
