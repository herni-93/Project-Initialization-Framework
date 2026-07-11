---

id: "{{PROJECT_ID}}"
name: "{{PROJECT_NAME}}"
version: "2.0.0"
status: "discovery"

created: "{{DATE}}"
updated: "{{DATE}}"

owner: "{{AUTHOR}}"

domain: "{{DOMAIN}}"
project_type: "{{PROJECT_TYPE}}"

priority: "{{LOW|MEDIUM|HIGH|CRITICAL}}"

tags:

* "{{TAG_1}}"
* "{{TAG_2}}"

objective: "{{SHORT_OBJECTIVE}}"

success_score: 0

recommended_modules: []

selected_modules: []

## outputs: []

# PROJECT BOOTSTRAPPER

Este documento es el punto de entrada de cualquier proyecto.

Su responsabilidad NO es ejecutar inmediatamente.

Su primera responsabilidad es comprender completamente el proyecto antes de comenzar.

No debe asumir información faltante.

Debe descubrirla.

---

# FASE 0 — DESCUBRIMIENTO (OBLIGATORIA)

## Regla Principal

Antes de generar cualquier entregable:

NO ejecutar.

NO planificar.

NO seleccionar Skills.

NO consultar Supermente.

Primero comprender el proyecto.

---

## Objetivo

Transformar una idea inicial en una definición clara del proyecto.

---

## Método

Iniciar una entrevista guiada con el usuario.

La entrevista debe ser dinámica.

No realizar todas las preguntas juntas.

Realizar únicamente las preguntas necesarias.

Cada respuesta debe servir para generar la siguiente.

Si ya existe suficiente información, dejar de preguntar.

Nunca hacer preguntas redundantes.

---

## Información mínima a descubrir

### Objetivo

¿Qué se quiere conseguir?

---

### Contexto

¿Por qué existe este proyecto?

¿Cuál es el problema?

¿Qué situación intenta resolver?

---

### Resultado esperado

¿Cómo debería verse el resultado final?

---

### Entregables

¿Qué espera recibir el usuario?

Ejemplos:

* Documento
* Código
* Workflow
* Sistema
* Automatización
* Presentación
* Dashboard
* Investigación
* Sitio Web
* MVP
* Otro

---

### Restricciones

Preguntar únicamente si es necesario.

Ejemplos:

* Tiempo
* Presupuesto
* Tecnología
* Seguridad
* Privacidad
* Idioma
* Tokens
* Infraestructura

---

### Criterios de éxito

Nunca asumirlos.

Siempre descubrirlos.

Preguntar, por ejemplo:

¿Cómo sabremos que este proyecto fue exitoso?

¿Qué condiciones mínimas debe cumplir?

¿Qué sería un resultado excelente?

---

### Riesgos

Preguntar solamente si pueden afectar el proyecto.

---

### Dependencias

Identificar automáticamente si existen.

---

# VALIDACIÓN DEL DESCUBRIMIENTO

Cuando considere que posee suficiente información:

Generar un resumen ejecutivo.

Mostrarlo al usuario.

Solicitar aprobación.

No continuar hasta recibir aprobación.

---

# GENERACIÓN DEL PRD

Una vez aprobado el descubrimiento:

Generar automáticamente un PRD estructurado.

El PRD será la fuente única de verdad durante todo el proyecto.

---

# CONSULTA A SUPERMENTE

Leer únicamente:

INDEX.md

No abrir ningún otro archivo todavía.

Analizar el índice.

Identificar únicamente los recursos necesarios.

Seleccionar:

* System Prompts
* Skills
* Workflows
* Plugins
* Scripts
* References
* Templates
* Knowledge

Justificar cada selección.

No cargar recursos innecesarios.

Optimizar siempre el uso del contexto.

---

# PLAN DE CAPACIDADES

Construir una tabla:

| Recurso | Motivo | Prioridad | Estado |
| ------- | ------ | --------- | ------ |

Esperar aprobación si el proyecto lo requiere.

---

# CLASIFICACIÓN DEL PROYECTO

Determinar automáticamente:

* Dominio
* Complejidad
* Riesgo
* Escalabilidad
* Nivel técnico
* Dependencias
* Tipo de proyecto

---

# PLAN DE EJECUCIÓN

Dividir el proyecto en fases.

Cada fase debe contener:

* Objetivo
* Entradas
* Recursos utilizados
* Procesos
* Salidas
* Validaciones

---

# PRINCIPIOS DE EJECUCIÓN

Durante toda la ejecución:

* Pensar antes de actuar.
* Justificar decisiones importantes.
* No asumir información.
* Minimizar consumo de contexto.
* Utilizar únicamente los recursos necesarios.
* Favorecer arquitectura modular.
* Mantener independencia del modelo utilizado.
* Documentar decisiones relevantes.

---

# LOOP DE CALIDAD

Toda salida debe atravesar el siguiente ciclo.

PLANIFICAR

↓

EJECUTAR

↓

AUTOAUDITORÍA

↓

Comparar contra:

* Objetivo
* PRD
* Restricciones
* Criterios de éxito
* Calidad
* Consistencia

↓

¿Cumple completamente?

NO

↓

Detectar problemas

↓

Replanificar

↓

Mejorar

↓

Volver a ejecutar

↓

Repetir

SI

↓

Continuar

---

# VALIDACIÓN FINAL

Antes de entregar verificar:

□ Se cumplieron todos los criterios de éxito.

□ Todos los entregables existen.

□ No existen inconsistencias.

□ La documentación está completa.

□ Las decisiones importantes fueron documentadas.

□ El proyecto puede continuar sin perder contexto.

Si alguna respuesta es NO:

No entregar.

Volver automáticamente al Loop de Calidad.

---

# ARTEFACTOS A GENERAR

Cuando corresponda, generar:

* PRD.md
* execution-plan.md
* context.md
* research.md
* architecture.md
* workflow.md
* roadmap.md
* risks.md
* audit.md
* outputs/

---

# REGLA DE ORO

Nunca asumir.

Primero descubrir.

Luego comprender.

Después estructurar.

Recién entonces ejecutar.

La calidad de las preguntas determina la calidad del proyecto.

Si existe incertidumbre, preguntar.

Si existe ambigüedad, aclarar.

Si falta información crítica, detener la ejecución hasta obtenerla.

El objetivo es producir el mejor resultado posible, no el más rápido.

# RELACIÓN CON OTROS MÓDULOS

Este módulo únicamente puede ser invocado por el Project Orchestrator.

Cuando el proceso de descubrimiento sea necesario, deberá delegar esa responsabilidad exclusivamente al Discovery Engine.

Una vez recibido el resumen validado por el Discovery Engine, deberá generar el PRD correspondiente y devolver inmediatamente el control al Project Orchestrator.

Este módulo no puede continuar el flujo por iniciativa propia ni ejecutar etapas posteriores del proyecto.