#!/usr/bin/env bash
# Reproduces this sample run. Execute from the repository root:
#   bash examples/sample-run/run.sh
set -euo pipefail
DIR=examples/sample-run/output
rm -rf "$DIR"
PIF="python3 -m pif --dir $DIR"

$PIF start "Quiero construir una plataforma SaaS para diseñadores freelance" \
  --name "Plataforma para diseñadores freelance" \
  --knowledge examples/sample-knowledge-base
$PIF answer success_criteria "Que los usuarios la usen"
$PIF answer success_criteria "100 diseñadores pagando la suscripción dentro de los 6 meses del lanzamiento"
$PIF answer deliverables "MVP web con portfolio, facturación y portal de clientes"
$PIF answer problem "Los diseñadores freelance usan entre 4 y 6 herramientas para gestionar clientes y facturas"
$PIF answer expected_result "Aplicación web desplegada y usada por un grupo de diseñadores beta"
$PIF reject --reason "Falta aclarar las restricciones"
$PIF answer constraints "Presupuesto máximo de 5000 USD; lanzamiento antes de marzo 2027"
$PIF approve   # executive summary
$PIF approve   # PRD
$PIF metrics --format md > "$DIR/metrics.md"
