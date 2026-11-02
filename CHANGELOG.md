# Changelog

Todos los cambios relevantes del proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[Versionado Semántico](https://semver.org/lang/es/). La versión del framework es también la
versión de cada módulo.

---

## [2.1.0] - 2026-11-02

### Agregado

- `AGENTS.md` y `CLAUDE.md`: punto de entrada operativo para agentes de IA, con el modelo de
  coordinación de roles y el protocolo paso a paso.
- Módulo **Knowledge Connector**: conexión opcional y de solo lectura a una base de conocimiento
  existente (Markdown/Obsidian, grafo JSON, Neo4j), con pregunta de consentimiento. Si no existe,
  se ignora.
- Implementación de referencia en Python (`pif/`), sin dependencias: máquina de estados, puntaje
  de incertidumbre, banco de preguntas, conector de conocimiento, generación del PRD, control de
  calidad del PRD, métricas y CLI (`python -m pif`).
- Plantillas: `prd.template.md`, `executive-summary.template.md`,
  `project-state.schema.json`, `knowledge.config.example.json`.
- Documentación nueva: `docs/medicion.md`, `docs/conector-de-conocimiento.md`,
  `docs/implementacion.md`.
- Ejemplos: base de conocimiento de muestra y salida real de una inicialización.
- Tests (`tests/`).

### Cambiado

- Instrucciones para la IA (módulos) en inglés; documentación para personas en español.
- Estados unificados: `waiting`, `bootstrap`, `discovery`, `validation`, `prd_generation`,
  `prd_review`, `completed`, `cancelled`, `error`. `approved` pasa a ser `prd_review`, con una
  aprobación explícita del PRD por parte del usuario.
- Archivos de `docs/` y `examples/` renombrados sin espacios, en minúsculas.
- El frontmatter de los módulos ahora es YAML válido y describe el módulo (no un proyecto).

### Corregido

- El Project Bootstrapper duplicaba la entrevista del Discovery Engine; ahora la delega.
- El Project Bootstrapper incluía planes de ejecución, loop de calidad y artefactos de etapas
  posteriores; quedan fuera del alcance de la inicialización.
- Instrucciones contradictorias sobre consultar un índice externo de recursos; ahora lo hace solo
  el Knowledge Connector, en una etapa definida.
- La documentación decía que los módulos nunca se comunican directamente, pero el Bootstrapper
  delegaba al Discovery Engine; ahora la delegación jerárquica está documentada en todos lados.
- "No saltear estados" contradecía el descubrimiento opcional; ahora el descubrimiento es
  condicional y la validación es obligatoria.
- El Discovery Engine "delegaba al Bootstrapper" y a la vez "devolvía el resumen"; ahora solo devuelve.
- Nadie aprobaba el PRD aunque el Orchestrator lo exigía; ahora existe `prd_review`.
- La estructura del repositorio en el README no coincidía con los archivos reales.

---

## [2.0.0]

### Agregado

- Arquitectura modular de inicialización de proyectos.
- Project Orchestrator como controlador central del flujo.
- Project Bootstrapper para inicializar el proyecto y generar el PRD.
- Discovery Engine para el descubrimiento adaptativo.
- Flujo determinista basado en estados.
- Documentación de arquitectura y flujo de ejecución.
- Ejemplos en varios dominios.

### Cambiado

- El sistema pasó de ser un generador de PRD a un framework completo de inicialización.
- Orquestación centralizada.
- Separación de descubrimiento, validación y generación de la especificación.

---

## Próximas versiones

- Componentes para la capa de ejecución (investigación, arquitectura, planificación, auditoría).
- Búsqueda semántica en la base de conocimiento.
