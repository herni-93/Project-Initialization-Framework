# Conector de conocimiento

> Guía para personas. La instrucción para la IA está en `modules/knowledge-connector.md` y el
> código en `pif/knowledge.py`.

## Qué hace

Si ya tenés tu información unificada en algún lado (un "segundo cerebro", una bóveda de
Obsidian, un grafo de conocimiento, una carpeta con system prompts, skills y workflows), el
framework se conecta a eso **en modo lectura** y lo usa para:

- arrancar desde lo que ya sabés del tema (notas, entrevistas, decisiones);
- respetar tu forma de trabajar (tus instrucciones globales, tus skills, tus workflows);
- proponer en el PRD qué recursos tuyos conviene usar en el proyecto, cada uno con su motivo.

Si no tenés nada, lo ignora por completo y no lo vuelve a mencionar. **Nunca crea una base nueva
ni escribe en la tuya.**

## Cómo encuentra tu base

En este orden:

1. **Ruta explícita**: `--knowledge ~/mi-cerebro` o la ruta que le respondas en la pregunta.
2. **Archivo de configuración**: `pif.knowledge.json` en la carpeta actual o
   `~/.config/pif/knowledge.json`. Ejemplo en `templates/knowledge.config.example.json`.
3. **Variable de entorno**: `PIF_KNOWLEDGE_PATH=~/mi-cerebro`.
4. **Detección automática** en carpetas comunes: `~/.claude`, `~/brain`, `~/second-brain`,
   `~/knowledge`, `~/notes`, `~/Obsidian`, `~/Documents/brain`, `~/Documents/Obsidian`.
   En este caso **siempre te pide permiso** antes de usarla.

Para desactivarlo: `PIF_KNOWLEDGE=off` o `"enabled": false` en la configuración.

## La pregunta que te hace

Durante el bootstrap se hace una sola pregunta:

- Si encontró algo: *"Encontré estas fuentes de conocimiento: … ¿Puedo consultarlas en modo
  lectura para este proyecto?"*
- Si no encontró nada: *"¿Ya tenés una base de conocimiento que deba consultar (segundo cerebro,
  notas, base de grafos, carpeta con system prompts o skills)? Pasame la ruta o respondé 'no'."*

## Qué tipos de fuente entiende

| Tipo | Ejemplo | Cómo la lee |
| --- | --- | --- |
| `markdown` | Carpeta de notas, Obsidian, `~/.claude` | Primero el índice (`INDEX.md`, `index.md` o `README.md`), después las categorías, y las notas solo si son relevantes |
| `json-graph` | `graph.json` con `nodes` y `edges` | Busca en etiquetas, texto y tags de los nodos, y suma los nodos vecinos |
| `neo4j` | Base Neo4j local o remota | Consultas Cypher de solo lectura por la API HTTP; las credenciales salen de variables de entorno |

Además, si el agente de IA ya tiene herramientas propias de memoria o de grafos (por ejemplo un
servidor MCP), las trata como una fuente más con las mismas reglas.

## Qué reconoce dentro de tu base

| Carpeta o archivo | Se interpreta como |
| --- | --- |
| `CLAUDE.md`, `AGENTS.md`, `SYSTEM.md` en la raíz | Instrucciones globales de trabajo (siempre se proponen) |
| `system-prompts/`, `prompts/` | System prompts |
| `skills/<nombre>/SKILL.md` | Skills |
| `workflows/` | Workflows |
| `agents/` | Agentes |
| `templates/`, `references/`, `scripts/`, `plugins/`, `commands/` | Material reutilizable |
| `knowledge/`, `notes/`, `wiki/` | Conocimiento del dominio |

Hay un ejemplo completo en `examples/sample-knowledge-base/`.

## Comandos útiles

```bash
python -m pif knowledge scan --knowledge ~/mi-cerebro           # qué fuentes y recursos encuentra
python -m pif knowledge query facturación diseñadores --knowledge ~/mi-cerebro
```

## Reglas de seguridad

- Solo lectura: nunca escribe, mueve ni borra nada en tu base.
- Lee como máximo 2.000 archivos y los primeros 4 KB de cada uno.
- En el PRD cita fragmentos cortos con su ruta; no copia notas completas.
- No copia credenciales ni datos personales.
- Si una fuente no responde, la saltea sin frenar la inicialización.
- Lo que encuentra se **propone**; vos lo aprobás junto con el resumen.
