# Flujo de ejecución

> Guía para personas. La versión que sigue la IA está en `modules/project-orchestrator.md`.

## Visión general

El Project Orchestrator es dueño del ciclo de vida. No hace el trabajo: lo delega, valida el
resultado y decide si el proyecto avanza. Ningún módulo avanza el flujo por su cuenta.

## Ciclo de inicialización

```text
Pedido del usuario
      │
      ▼
Project Orchestrator ─────────────── estado: bootstrap
      │
      ▼
Project Bootstrapper
  ├─ clasifica el proyecto
  ├─ Knowledge Connector: ¿hay una base de conocimiento? (pregunta una vez)
  └─ mide la claridad (0-100)
      │
      ▼
¿Claridad suficiente?
 ┌────┴─────┐
 No         Sí
 │          │
 ▼          │
Discovery Engine ── estado: discovery
(una pregunta por vez)
 │          │
 └────┬─────┘
      ▼
Resumen ejecutivo ── estado: validation
¿El usuario lo aprueba?
 ├─ No → vuelve a discovery con los cambios
 └─ Sí
      ▼
Project Bootstrapper genera el PRD ── estado: prd_generation
      ▼
Control de calidad del PRD
      ▼
El usuario revisa el PRD ── estado: prd_review
 ├─ Cambios → vuelve a discovery
 └─ Aprobado
      ▼
Project Orchestrator: checklist final y handoff ── estado: completed
```

## Etapas

1. **Recepción**: el Orchestrator recibe el pedido y pasa a `bootstrap`.
2. **Bootstrap**: el Bootstrapper toma todo lo que el pedido ya dice, clasifica el proyecto,
   resuelve la base de conocimiento y calcula la claridad.
3. **Descubrimiento** (solo si hace falta): el Discovery Engine hace una pregunta por vez,
   empezando por los campos críticos. Termina apenas la claridad llega a 80 con los campos
   críticos completos, al llegar a 12 preguntas, o cuando el usuario pide terminar.
4. **Validación** (siempre): se muestra el resumen ejecutivo. Sin aprobación no se avanza.
   Un resumen con un campo crítico incompleto no se puede aprobar.
5. **Generación del PRD**: el Bootstrapper completa la plantilla solo con datos aprobados.
   Lo que falta va a "Open Questions".
6. **Control de calidad**: el PRD debe tener todas las secciones, ningún `{{marcador}}`
   sin completar y criterios de éxito medibles.
7. **Revisión del PRD**: el usuario lo aprueba o pide cambios.
8. **Cierre**: el Orchestrator verifica el checklist final, marca el PRD como aprobado y
   escribe `handoff.json` para la siguiente capa.

## Modelo de delegación

Las responsabilidades bajan y el control siempre vuelve hacia arriba:

```text
Orchestrator → Bootstrapper → (Knowledge Connector | Discovery Engine)
Orchestrator ← Bootstrapper ←
```

## Reglas

- Cada etapa depende de que la anterior haya terminado bien.
- Ningún módulo hace el trabajo de otro.
- La validación es obligatoria antes del PRD.
- Solo el Orchestrator cambia el estado.
- No se avanza mientras quede incertidumbre crítica.

## Resultado esperado

- Una definición del proyecto validada (`executive-summary.md`).
- Un PRD aprobado (`PRD.md`).
- Un paquete de traspaso (`handoff.json`) con métricas.

En ese punto termina la responsabilidad del framework y el control pasa a la siguiente capa
de planificación o ejecución.
