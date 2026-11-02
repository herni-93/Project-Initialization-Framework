# Principios de diseño

> Guía para personas. Estos principios se aplican igual sin importar el dominio o el modelo de IA.

## 1. Descubrir antes de ejecutar

No se ejecuta nada hasta entender el problema. Si hay incertidumbre, se descubre primero.

## 2. Nunca suponer

La información faltante no se inventa. Si falta, se pregunta; si no se responde, queda como
pregunta abierta en el PRD.

## 3. Responsabilidad única

Cada componente tiene una sola responsabilidad. El comportamiento complejo surge de la
orquestación, no de componentes que hacen de todo.

## 4. Orquestación sobre autonomía

Los componentes no controlan el flujo. El Orchestrator delega, valida y decide cuándo se avanza.

## 5. Validar antes de avanzar

Cada hito importante requiere validación. El PRD nunca se genera con información sin aprobar.

## 6. Flujo determinista

El mismo estado del proyecto siempre produce el mismo comportamiento. La máquina de estados
rechaza cualquier transición no definida.

## 7. Delegación explícita

Ningún componente se saltea a otro ni continúa el flujo por su cuenta. Toda tarea delegada
devuelve el control.

## 8. Arquitectura modular

Se agregan capacidades extendiendo la orquestación, sin cambiar las responsabilidades existentes.

## 9. Independencia del modelo

Las instrucciones describen un proceso, no capacidades de un modelo en particular.

## 10. Eficiencia de contexto

Se carga solo lo necesario para la etapa actual: el módulo del rol activo, el índice de la base
de conocimiento antes que sus notas, y fragmentos cortos en lugar de documentos completos.

## 11. Medir, no opinar

La incertidumbre tiene un puntaje (0-100) y cada inicialización deja métricas. "Está claro" se
decide con un número y con la aprobación del usuario, no por intuición.

## 12. Usar lo que ya existe

Si el usuario ya tiene una base de conocimiento, se consulta (con permiso y en modo lectura).
Si no la tiene, se ignora. Nunca se crea una nueva.

## Filosofía

> **Un proyecto solo avanza cuando fue entendido con claridad.**
