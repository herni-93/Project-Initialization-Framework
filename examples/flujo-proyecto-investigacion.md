# Ejemplo: proyecto de investigación

## Pedido inicial

> "Quiero investigar cómo las empresas están adoptando la automatización con IA en sus procesos internos."

## 1. Bootstrap

El Bootstrapper clasifica el proyecto como `research` ("investigar"). El Knowledge Connector
detecta una carpeta `~/brain` y pide permiso:

> "Encontré estas fuentes de conocimiento: ~/brain. ¿Puedo consultarlas en modo lectura?"

```bash
python -m pif --dir .pif start "Quiero investigar cómo las empresas adoptan la automatización con IA"
python -m pif --dir .pif answer knowledge_consent "sí"
```

Con permiso, las notas previas del usuario sobre el tema se van a proponer en el resumen.

## 2. Descubrimiento adaptativo

- **Criterios de éxito**: ¿qué haría útil a la investigación? (por ejemplo, 20 empresas analizadas
  antes de una fecha).
- **Entregables**: ¿en qué formato: informe, dataset, presentación?
- **Problema**: ¿qué pregunta tiene que responder y sobre qué industrias o mercados?
- **Contexto**: ¿qué fuentes y metodología usar o evitar?

## 3. Validación

El resumen incluye objetivo, alcance, metodología, entregables, restricciones, criterios de éxito
y las notas relevantes encontradas. Si hay cambios, solo se revisan las partes afectadas.

## 4. PRD

El PRD define el alcance, los entregables, los criterios medibles y las preguntas abiertas.
Con la aprobación del usuario, la inicialización termina.

## Resultado

- ✅ Alcance de la investigación validado
- ✅ Conocimiento previo del usuario reutilizado
- ✅ PRD aprobado y listo para ejecutar
