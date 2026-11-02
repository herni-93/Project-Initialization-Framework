# Project Initialization Framework

> Framework modular para inicializar proyectos asistidos por IA: descubre lo que falta,
> mide la incertidumbre, valida con el usuario y recién entonces genera un PRD aprobado.
> Es independiente del modelo (Claude, GPT, Gemini, etc.).

El repositorio tiene dos partes:

1. **Instrucciones para agentes de IA** (en inglés): `AGENTS.md`, `modules/` y `templates/`.
   Un agente que abre este repo las lee y sabe cómo coordinar la inicialización.
2. **Implementación de referencia** (Python, sin dependencias): `pif/`. Hace cumplir las reglas
   en código: máquina de estados, puntaje de incertidumbre, conexión opcional a tu base de
   conocimiento, generación y control de calidad del PRD, y métricas.

La documentación para personas (este README y `docs/`) está en español y sirve solo como guía.

---

## Por qué existe

La mayoría de los proyectos con IA no fallan por la implementación: fallan porque se empieza a
ejecutar antes de entender el problema. Requisitos incompletos, supuestos ocultos y objetivos
vagos llevan a planes malos y a iteraciones perdidas.

El framework agrega una etapa previa obligatoria:

> **Nunca ejecutar antes de entender el problema.**

---

## Cómo usarlo

### Opción A: con un agente de IA (uso principal)

1. Cloná el repo.
2. Abrilo con tu agente (Claude Code lee `CLAUDE.md`, otros agentes leen `AGENTS.md`).
3. Pedile: *"Inicializá un proyecto nuevo: quiero …"*.

El agente toma el rol de Orchestrator, te hace una pregunta por vez, te muestra un resumen
para aprobar y genera el PRD. Si tenés Python instalado, usa la CLI `pif` para guardar el estado
y medir el proceso.

### Opción B: en la terminal

```bash
python -m pif run "Quiero una plataforma SaaS para diseñadores freelance"
```

### Opción C: paso a paso (lo que usa el agente)

```bash
python -m pif --dir .pif start "Quiero una plataforma SaaS para diseñadores freelance"
python -m pif --dir .pif answer knowledge_source "no"
python -m pif --dir .pif answer success_criteria "100 usuarios pagos en 6 meses"
python -m pif --dir .pif status     # muestra la próxima pregunta y el puntaje
python -m pif --dir .pif approve    # aprueba el resumen y después el PRD
python -m pif --dir .pif metrics --format md
```

Requisitos: Python 3.9 o superior. No hace falta instalar nada. Opcional: `pip install -e .`
para tener el comando `pif`.

Tests: `python -m unittest discover -s tests`.

---

## Arquitectura

```text
Usuario
  │
  ▼
Project Orchestrator ── único dueño del estado
  │ delega
  ▼
Project Bootstrapper ── clasifica, mide claridad, genera el PRD
  │                 │
  ▼                 ▼
Knowledge Connector  Discovery Engine
(tu base de          (entrevista adaptativa,
 conocimiento,        resumen y validación)
 solo lectura)
```

Cada módulo hace una sola cosa y devuelve el control a quien lo llamó.
Detalle en [docs/arquitectura.md](docs/arquitectura.md).

## Estados

```text
waiting → bootstrap → discovery → validation → prd_generation → prd_review → completed
                  └──────────────→ validation        (si ya hay información suficiente)
          validation / prd_review → discovery        (si el usuario pide cambios)
          cualquier estado activo → cancelled | error  (error se reanuda desde el último estado válido)
```

El descubrimiento puede saltearse; la validación nunca. Ver
[docs/maquina-de-estados.md](docs/maquina-de-estados.md).

## Conexión con tu base de conocimiento

Si ya tenés un "segundo cerebro", una bóveda de notas, un grafo de conocimiento o una carpeta con
system prompts y skills, el framework lo detecta (o te pregunta dónde está), te pide permiso y lo
consulta **solo en modo lectura**. Así arranca desde lo que ya sabés y desde tu forma de trabajar.
Si no tenés nada, lo ignora por completo. Nunca crea una base nueva.
Ver [docs/conector-de-conocimiento.md](docs/conector-de-conocimiento.md).

## Medición

La incertidumbre se mide con un puntaje de claridad de 0 a 100. El descubrimiento termina con
80 puntos o más y los campos críticos completos. Cada paso queda registrado y se puede ver un
reporte de métricas con objetivos. Ver [docs/medicion.md](docs/medicion.md).

---

## Estructura del repositorio

```text
.
├── AGENTS.md                  instrucciones para agentes de IA (inglés)
├── CLAUDE.md                  apunta a AGENTS.md
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── modules/                   roles del framework (inglés)
│   ├── project-orchestrator.md
│   ├── project-bootstrapper.md
│   ├── discovery-engine.md
│   └── knowledge-connector.md
├── templates/                 plantillas que completa la IA (inglés)
│   ├── prd.template.md
│   ├── executive-summary.template.md
│   ├── project-state.schema.json
│   └── knowledge.config.example.json
├── pif/                       implementación de referencia (Python)
├── tests/
├── docs/                      guía para personas (español)
│   ├── arquitectura.md
│   ├── flujo-de-ejecucion.md
│   ├── maquina-de-estados.md
│   ├── responsabilidades-de-modulos.md
│   ├── principios-de-diseno.md
│   ├── conector-de-conocimiento.md
│   ├── medicion.md
│   └── implementacion.md
└── examples/
    ├── flujo-proyecto-software.md
    ├── flujo-proyecto-marketing.md
    ├── flujo-proyecto-investigacion.md
    ├── sample-knowledge-base/     base de conocimiento de ejemplo
    └── sample-run/                salida real de una inicialización
```

## Convención de idiomas

| Qué | Idioma |
| --- | --- |
| Instrucciones para la IA (`AGENTS.md`, `modules/`, `templates/`) | Inglés |
| Código y comentarios (`pif/`, `tests/`) | Inglés |
| Documentación para personas (`README.md`, `docs/`, `examples/*.md`, `CONTRIBUTING.md`, `CHANGELOG.md`) | Español |

El agente le habla al usuario en su idioma, aunque las instrucciones estén en inglés.

## Componentes

| Estado | Componente | Responsabilidad |
| --- | --- | --- |
| ✅ | Project Orchestrator | Controla el ciclo de vida y el estado |
| ✅ | Project Bootstrapper | Clasifica, mide claridad y genera el PRD |
| ✅ | Discovery Engine | Entrevista adaptativa, resumen y validación |
| ✅ | Knowledge Connector | Consulta opcional de tu base de conocimiento |

## Hoja de ruta

Componentes posibles para la capa que recibe el PRD: Research Engine, Architecture Generator,
Risk Analyzer, Task Planner, Workflow Generator, Execution Orchestrator y QA & Audit Engine.
Se agregan sin cambiar las responsabilidades de los módulos actuales.

## Licencia

MIT. Ver `LICENSE`.
