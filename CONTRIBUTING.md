# Guía de contribución

Gracias por contribuir al Project Initialization Framework.
Cada componente tiene una responsabilidad clara; las contribuciones tienen que respetar eso.

## Convención de idiomas

| Qué | Idioma |
| --- | --- |
| Instrucciones para la IA: `AGENTS.md`, `CLAUDE.md`, `modules/`, `templates/` | Inglés |
| Código, comentarios y tests: `pif/`, `tests/` | Inglés |
| Documentación para personas: `README.md`, `docs/`, `examples/*.md`, este archivo, `CHANGELOG.md` | Español |

Los nombres de archivo van en minúsculas y con guiones, sin espacios.

## Principios

Antes de agregar funcionalidad:

- Definí la responsabilidad con claridad.
- No te superpongas con un componente existente.
- Mantené el flujo determinista: los estados y transiciones nuevos van en `pif/states.py`,
  `modules/project-orchestrator.md` y `docs/maquina-de-estados.md`, siempre juntos.
- Mantené los componentes independientes.
- No agregues dependencias externas a `pif/` (solo librería estándar).

## Componentes nuevos

Un componente nuevo debe:

- tener una sola responsabilidad;
- ser invocado a través de la cadena de orquestación;
- devolver el control al terminar;
- no modificar flujos ajenos.

Y debe incluir:

- `modules/<nombre>.md` (en inglés) con frontmatter YAML válido: `id`, `name`, `version`, `type`,
  `status`, `description`, `invoked_by`, `delegates_to`, `inputs`, `outputs`;
- su descripción en `docs/responsabilidades-de-modulos.md` (en español);
- implementación y tests en `pif/` y `tests/` si cambia el comportamiento.

## Antes de abrir un pull request

- [ ] `python -m unittest discover -s tests` pasa.
- [ ] La documentación en español y las instrucciones en inglés dicen lo mismo.
- [ ] No hay contradicciones entre módulos (quién invoca a quién, quién cambia el estado).
- [ ] `CHANGELOG.md` actualizado.
- [ ] Explicaste las decisiones de arquitectura.

## Filosofía

- Entender antes de ejecutar.
- Validación explícita.
- Arquitectura modular.
- Mínimos supuestos.
