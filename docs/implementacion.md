# Implementación

> Guía para personas sobre cómo usar e integrar el framework. Las instrucciones operativas para
> la IA están en `AGENTS.md`.

## Tres formas de usarlo

### 1. Con un agente de IA

Abrí el repositorio con tu agente (Claude Code lee `CLAUDE.md`, que a su vez carga `AGENTS.md`;
otros agentes leen `AGENTS.md` directamente) y pedile que inicialice un proyecto. El agente:

1. actúa como Orchestrator y carga cada módulo solo cuando lo necesita;
2. usa la CLI `pif` para guardar el estado, medir la claridad y registrar métricas;
3. te habla en tu idioma, una pregunta por vez;
4. te muestra el resumen y el PRD para que los apruebes.

Para usarlo en otro proyecto, apuntá el workspace a ese proyecto:
`python -m pif --dir ~/mi-proyecto/.pif start "..."`.

### 2. En la terminal (modo interactivo)

```bash
python -m pif run "Quiero lanzar una campaña para un producto de IA" --knowledge ~/mi-cerebro
```

Escribí `:done` para cerrar el descubrimiento antes y `:cancel` para salir.

### 3. Desde tu propio código

```python
from pif.orchestrator import Orchestrator
from pif.workspace import Workspace

orch = Orchestrator(Workspace("mi-proyecto/.pif"))
status = orch.start(
    "Quiero una plataforma SaaS para diseñadores freelance",
    fields={"deliverables": "MVP web con portfolio y facturación"},  # lo que el pedido ya dice
    auto_detect=False,
)
while status["next_question"]:
    pregunta = status["next_question"]
    respuesta = input(pregunta["text"] + "\n> ")
    status = orch.answer(pregunta["field"], respuesta)

print(orch.ws.read("executive-summary.md"))
orch.approve()                                 # resumen aprobado → genera el PRD
print(orch.ws.read("PRD.md"))
orch.approve()                                 # PRD aprobado → completed + handoff.json
```

Si una regla del framework bloquea una acción (por ejemplo, aprobar con un campo crítico vacío),
se lanza `GuardError` y el estado no cambia.

## Referencia de la CLI

| Comando | Qué hace |
| --- | --- |
| `start "<pedido>" [--field CAMPO=VALOR] [--knowledge RUTA] [--no-auto-detect]` | Inicia y hace el bootstrap |
| `status` | Estado, claridad, próxima pregunta y próxima acción |
| `next` | Solo la próxima pregunta |
| `answer CAMPO "respuesta"` | Registra una respuesta (o un cambio durante la validación) |
| `summary` | Cierra el descubrimiento y genera el resumen |
| `approve` | Aprueba el resumen o el PRD |
| `reject --reason "..."` | Rechaza el resumen o el PRD y vuelve al descubrimiento |
| `cancel` / `resume` | Cancela / reanuda después de un error |
| `check-prd [ARCHIVO]` | Control de calidad de un PRD |
| `metrics [--format md]` | Reporte de métricas |
| `knowledge scan` / `knowledge query TÉRMINOS` | Inspecciona la base de conocimiento |
| `run "<pedido>"` | Modo interactivo completo |

Opción global: `--dir` (por defecto `.pif`). Los comandos devuelven JSON; el código de salida 2
significa que una regla del framework bloqueó la acción.

## Archivos que genera

| Archivo | Contenido |
| --- | --- |
| `.pif/state.json` | Estado actual (formato en `templates/project-state.schema.json`) |
| `.pif/events.jsonl` | Registro de eventos para las métricas |
| `.pif/executive-summary.md` | Resumen para validar |
| `.pif/PRD.md` | PRD (borrador o aprobado) |
| `.pif/handoff.json` | Paquete para la siguiente capa |
| `.pif/archive/` | Inicializaciones anteriores terminadas o canceladas |

Hay un ejemplo real en `examples/sample-run/`.

## Estructura del código

| Archivo | Responsabilidad |
| --- | --- |
| `pif/states.py` | Estados y transiciones permitidas |
| `pif/uncertainty.py` | Campos, pesos y puntaje de claridad |
| `pif/questions.py` | Banco de preguntas por tipo de proyecto |
| `pif/knowledge.py` | Knowledge Connector (Markdown, grafo JSON, Neo4j) |
| `pif/discovery.py` | Discovery Engine |
| `pif/bootstrapper.py` | Project Bootstrapper |
| `pif/orchestrator.py` | Project Orchestrator |
| `pif/documents.py` | Resumen, PRD y control de calidad |
| `pif/metrics.py` | Métricas y objetivos |
| `pif/cli.py` | Línea de comandos |

## Tests

```bash
python -m unittest discover -s tests
```

## Límites de la implementación de referencia

- Es determinista: no usa un modelo de lenguaje. El banco de preguntas es fijo por tipo de proyecto;
  el agente de IA las adapta y las traduce al hablar con el usuario.
- La búsqueda en la base de conocimiento es por palabras clave, no semántica.
- Para usar las plantillas, ejecutala desde el repositorio clonado o con `pip install -e .`.
