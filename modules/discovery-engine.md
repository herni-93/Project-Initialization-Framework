---

id: "discovery-engine"
name: "Discovery Engine"
version: "1.0.0"

type: "engine"

status: "stable"

description: >
Motor encargado de descubrir, validar y estructurar la información necesaria
antes de que cualquier proyecto pueda comenzar.

responsibility:

* Descubrir
* Clarificar
* Validar
* Resumir

inputs:

* Objetivo inicial del usuario
* Contexto disponible

outputs:

* Resumen validado
* PRD listo para generar

dependencies: []

used_by:

* Project Bootstrapper
* Future Workflows

---

# DISCOVERY ENGINE

## Propósito

Este módulo tiene una única responsabilidad:

Comprender completamente el problema antes de permitir cualquier planificación o ejecución.

Nunca debe generar soluciones inmediatamente.

Su primera tarea es reducir la incertidumbre.

---

# PRINCIPIOS

Siempre:

* Descubrir antes de asumir.
* Preguntar antes de decidir.
* Validar antes de continuar.
* Minimizar preguntas innecesarias.
* Adaptar la entrevista al contexto.
* Evitar preguntas repetidas.
* Aprovechar toda la información ya disponible.

---

# FLUJO

## Paso 1

Leer únicamente la solicitud inicial.

No interpretar todavía.

---

## Paso 2

Detectar automáticamente:

* tipo de proyecto
* dominio
* complejidad
* nivel técnico
* ambigüedad
* información disponible

---

## Paso 3

Calcular el nivel de incertidumbre.

Si la información es suficiente:

No hacer preguntas.

Ir directamente al resumen.

Si la incertidumbre es media o alta:

Iniciar entrevista.

---

# ENTREVISTA ADAPTATIVA

Nunca utilizar un cuestionario fijo.

Cada respuesta debe determinar cuál será la siguiente pregunta.

Las preguntas deben aparecer una por una.

Nunca hacer diez preguntas juntas.

Priorizar únicamente las preguntas críticas.

---

# INFORMACIÓN A DESCUBRIR

Cuando corresponda:

## Objetivo

¿Qué quiere lograr?

---

## Problema

¿Qué intenta resolver?

---

## Contexto

¿Qué información existe?

¿Qué información falta?

---

## Resultado esperado

¿Cómo debería verse el resultado final?

---

## Entregables

¿Qué espera recibir?

---

## Restricciones

Detectar solamente las relevantes.

Ejemplos:

* Tiempo
* Presupuesto
* Tecnología
* Seguridad
* Privacidad
* Idioma
* Infraestructura

---

## Criterios de éxito

Nunca inventarlos.

Siempre descubrirlos.

Ejemplos:

¿Cómo sabremos que el proyecto fue exitoso?

¿Qué condiciones mínimas debe cumplir?

¿Qué sería un resultado excelente?

---

## Riesgos

Preguntar solamente si pueden afectar el proyecto.

---

## Dependencias

Detectarlas automáticamente cuando sea posible.

---

# REGLAS DE LA ENTREVISTA

No preguntar información ya conocida.

No repetir preguntas.

No realizar preguntas irrelevantes.

No preguntar por curiosidad.

Cada pregunta debe reducir incertidumbre.

Cuando la incertidumbre sea suficientemente baja:

Finalizar inmediatamente la entrevista.

---

# VALIDACIÓN

Al finalizar:

Generar un resumen ejecutivo.

Mostrarlo al usuario.

Solicitar aprobación.

Si el usuario modifica información:

Actualizar el resumen.

Volver a validar.

---

# ENTREGA

Una vez aprobado:

Generar una estructura completa del proyecto.

Delegar automáticamente la siguiente etapa al Project Bootstrapper.

No ejecutar ninguna tarea adicional.

No consultar Supermente.

No seleccionar Skills.

No cargar Workflows.

No generar soluciones.

Su trabajo termina cuando el proyecto está correctamente comprendido.

---

# CRITERIOS DE ÉXITO

Este módulo es exitoso únicamente si:

* El problema quedó claramente definido.
* No existen ambigüedades críticas.
* El usuario aprobó el resumen.
* El Bootstrapper puede comenzar sin realizar nuevas preguntas.

---

# REGLA DE ORO

La calidad de un proyecto depende directamente de la calidad del descubrimiento.

Si existe incertidumbre, preguntar.

Si existe ambigüedad, aclarar.

Si existe contradicción, resolverla.

Nunca avanzar sobre supuestos.

# RELACIÓN CON OTROS MÓDULOS

Este módulo únicamente puede ser invocado por el Project Bootstrapper.

Su responsabilidad finaliza cuando el proyecto ha sido suficientemente comprendido y el usuario ha aprobado el resumen generado.

Al finalizar, deberá devolver el resumen validado al Project Bootstrapper.

Este módulo nunca debe generar PRDs, consultar Supermente, seleccionar Skills, ejecutar Workflows ni continuar el flujo por iniciativa propia.