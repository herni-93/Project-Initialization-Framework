# Corrida de ejemplo

Salida real de la implementación de referencia para el
[ejemplo de software](../flujo-proyecto-software.md), usando la
[base de conocimiento de muestra](../sample-knowledge-base/).

Para reproducirla, desde la raíz del repositorio:

```bash
bash examples/sample-run/run.sh
```

| Archivo | Contenido |
| --- | --- |
| `output/state.json` | Estado final del proyecto |
| `output/events.jsonl` | Cada paso registrado (preguntas, transiciones, aprobaciones) |
| `output/executive-summary.md` | Resumen que se validó |
| `output/PRD.md` | PRD aprobado |
| `output/handoff.json` | Paquete para la siguiente capa |
| `output/metrics.md` | Métricas y objetivos |
