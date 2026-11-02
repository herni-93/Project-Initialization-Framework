# Ejemplo: proyecto de software

> Ejemplo guiado. La salida real de este caso está en [sample-run/](sample-run/).

## Pedido inicial

> "Quiero construir una plataforma SaaS para diseñadores freelance."

## 1. Bootstrap

El Project Orchestrator recibe el pedido, pasa a `bootstrap` y delega en el Project Bootstrapper.

El Bootstrapper:

- clasifica el proyecto como `software` (palabras "plataforma" y "SaaS");
- toma el pedido como objetivo inicial → claridad **20/100**;
- delega en el Knowledge Connector, que encuentra la base de conocimiento indicada con `--knowledge`.

```bash
python -m pif --dir .pif start "Quiero construir una plataforma SaaS para diseñadores freelance" \
  --knowledge examples/sample-knowledge-base
```

Como la claridad es baja, el Orchestrator pasa a `discovery`.

## 2. Descubrimiento adaptativo

El Discovery Engine hace **una pregunta por vez**, empezando por los campos críticos:

| # | Campo | Pregunta (adaptada a software) | Claridad después |
| --- | --- | --- | --- |
| 1 | Criterios de éxito | ¿Cómo sabremos que el proyecto fue exitoso? Un número, porcentaje o fecha. | 30 (no es medible: "que los usuarios la usen") |
| 2 | Criterios de éxito | Seguimiento: ¿podés agregar un número, porcentaje o fecha? | 40 |
| 3 | Entregables | ¿Qué es el MVP? ¿Qué funciones tiene que tener la primera versión? | 55 |
| 4 | Problema | ¿Quiénes son los usuarios y qué problema les resuelve? | 70 |
| 5 | Resultado esperado | ¿Cómo debería verse el resultado final? | 80 → listo |

Con 80 puntos y los campos críticos completos, la entrevista termina sola.

## 3. Validación

Se muestra `executive-summary.md`, con los recursos de la base de conocimiento que se proponen
(instrucciones globales, la skill `saas-mvp-scoping`, las entrevistas a diseñadores).

El usuario pide aclarar las restricciones:

```bash
python -m pif --dir .pif reject --reason "Falta aclarar las restricciones"
python -m pif --dir .pif answer constraints "Presupuesto máximo de 5000 USD; lanzamiento antes de marzo 2027"
python -m pif --dir .pif approve
```

## 4. PRD

El Bootstrapper genera `PRD.md` solo con lo aprobado. Contexto y riesgos quedan como preguntas
abiertas. El control de calidad verifica las secciones y que los criterios sean medibles.

```bash
python -m pif --dir .pif approve
python -m pif --dir .pif metrics --format md
```

## Resultado

- ✅ Proyecto inicializado (`completed`)
- ✅ Claridad 20 → 90 en 6 preguntas
- ✅ PRD aprobado con recursos propios del usuario
- ✅ `handoff.json` listo para la capa de planificación
