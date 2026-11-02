# Medición

> Guía para personas. El cálculo está en `pif/uncertainty.py` y `pif/metrics.py`.

## 1. Puntaje de claridad (incertidumbre)

Cada campo del descubrimiento vale puntos. Un campo completo suma su peso entero, uno incompleto
la mitad y uno vacío nada.

| Campo | Peso | Crítico |
| --- | --- | --- |
| Objetivo (`objective`) | 20 | Sí |
| Criterios de éxito (`success_criteria`) | 20 | Sí |
| Entregables (`deliverables`) | 15 | Sí |
| Problema (`problem`) | 15 | No |
| Resultado esperado (`expected_result`) | 10 | No |
| Restricciones (`constraints`) | 10 | No |
| Contexto (`context`) | 5 | No |
| Riesgos (`risks`) | 5 | No |
| Dependencias (`dependencies`) | 0 (se detectan, no se preguntan) | No |

- **Claridad** = suma de pesos × puntaje (0 a 100). **Incertidumbre** = 100 − claridad.
- Nivel de incertidumbre: baja (≤ 20), media (≤ 50), alta (> 50).
- Una respuesta de menos de 8 caracteres cuenta como incompleta.
- Los criterios de éxito sin un número, porcentaje o fecha cuentan como incompletos.
- "ninguno" o "none" completa un campo opcional, pero nunca uno crítico.

**El descubrimiento termina** cuando la claridad llega a 80 y los tres campos críticos están
completos, o al llegar a 12 preguntas, o cuando el usuario pide terminar.

Ejemplo:

```python
from pif.uncertainty import assess

result = assess({
    "objective": "Plataforma SaaS para diseñadores freelance",
    "deliverables": "MVP web con portfolio y facturación",
    "success_criteria": "100 usuarios pagos en 6 meses",
    "problem": "Usan 5 herramientas distintas para clientes y facturas",
    "expected_result": "App desplegada usada por diseñadores beta",
})
print(result.clarity, result.ready)   # 80 True
```

## 2. Métricas de cada inicialización

Cada paso queda registrado en `.pif/events.jsonl`. El reporte se ve con:

```bash
python -m pif --dir .pif metrics --format md
```

| Métrica | Qué indica |
| --- | --- |
| `clarity_initial` → `clarity_final` | Cuánto se entendió desde el pedido hasta el PRD |
| `questions_answered` | Cuántas preguntas hicieron falta |
| `clarity_gain_per_question` | Qué tan útiles fueron las preguntas |
| `discovery_skipped` | Si el pedido ya era suficiente |
| `summary_rejections` | Cuántas veces el resumen no reflejaba lo que el usuario quería |
| `prd_rejections` | Cuántas veces el PRD no reflejaba el resumen aprobado |
| `seconds_to_first_prd`, `seconds_to_completion` | Tiempo hasta el PRD y hasta la aprobación |
| `knowledge_status`, `resources_selected` | Si se usó la base de conocimiento y cuántos recursos aportó |
| `module_errors` | Fallas de módulos |

## 3. Objetivos

| Métrica | Objetivo | Por qué |
| --- | --- | --- |
| `clarity_final` | ≥ 80 | El proyecto se entendió antes del PRD |
| `questions_answered` | ≤ 10 | No se cansó al usuario |
| `summary_rejections` | ≤ 1 | El resumen reflejó lo que el usuario quería |
| `prd_rejections` | ≤ 1 | El PRD fue fiel al resumen |
| `module_errors` | = 0 | Ningún módulo falló |

El reporte marca cada objetivo como cumplido o no.

## 4. Control de calidad del PRD

```bash
python -m pif check-prd ruta/al/PRD.md
```

Verifica que el PRD tenga todas las secciones de la plantilla, ningún `{{marcador}}` sin
completar, objetivo, entregables y criterios de éxito completos, y al menos un criterio medible.
Sirve también para PRDs escritos a mano o por otro agente.

## 5. Medir después de la inicialización

El framework termina con el PRD aprobado, pero conviene medir qué tan bueno fue:

- **Cambios al PRD después de aprobado**: con el PRD versionado en git,
  `git log --oneline -- PRD.md` muestra cuántas veces se tuvo que corregir. Lo ideal es cero
  cambios en objetivo, entregables y criterios de éxito.
- **Criterios de éxito cumplidos**: al cerrar el proyecto, comparar cada criterio medible del
  PRD contra el resultado real.
