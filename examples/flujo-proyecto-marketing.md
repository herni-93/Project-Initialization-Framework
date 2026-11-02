# Ejemplo: proyecto de marketing

## Pedido inicial

> "Necesito una campaña de lanzamiento para un producto nuevo de IA."

## 1. Bootstrap

El Bootstrapper clasifica el proyecto como `marketing` ("campaña", "lanzamiento"). No hay base
de conocimiento configurada, así que el Knowledge Connector hace su única pregunta:

> "¿Ya tenés una base de conocimiento que deba consultar? Pasame la ruta o respondé 'no'."

El usuario responde "no" y el conector no se vuelve a mencionar.

```bash
python -m pif --dir .pif start "Necesito una campaña de lanzamiento para un producto nuevo de IA"
python -m pif --dir .pif answer knowledge_source "no"
```

## 2. Descubrimiento adaptativo

Las preguntas se adaptan al tipo de proyecto:

- **Criterios de éxito**: ¿qué KPIs definen el éxito? (por ejemplo, 500 registros en 30 días).
- **Entregables**: ¿qué canales y piezas tiene que incluir la campaña?
- **Problema**: ¿qué producto se promociona y a qué público?
- **Restricciones**: ¿qué presupuesto y plazo tiene la campaña?

La entrevista termina apenas la claridad llega a 80 con los campos críticos completos.

## 3. Validación

Se muestra el resumen ejecutivo. Si el usuario cambia algo (por ejemplo, el canal principal),
se registra con `pif answer deliverables "..."` y el resumen se regenera.

## 4. PRD

Con el resumen aprobado se genera el PRD: objetivos de la campaña, restricciones, entregables,
KPIs medibles y preguntas abiertas. El usuario lo revisa y lo aprueba.

## Resultado

- ✅ Campaña definida y validada
- ✅ KPIs medibles en el PRD
- ✅ Lista para pasar a planificación
