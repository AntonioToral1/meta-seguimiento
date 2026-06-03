@echo off
REM ── Actualización diaria del dashboard de metaliados ──────────────────────
REM Ejecutar desde: C:\Users\mgrdatos\Documents\META_TORAL_local\

cd /d C:\Users\mgrdatos\Documents\META_TORAL_local

echo [%date% %time%] Generando datos...
python generar_seguimiento_metaliados.py >> seguimiento_web\actualizar.log 2>&1

echo [%date% %time%] Subiendo a GitHub...
cd seguimiento_web
git add data\seguimiento_metaliados.csv data\seguimiento_cosechas.csv app.py
git commit -m "Actualización automática %date%" >> actualizar.log 2>&1
git push >> actualizar.log 2>&1

echo [%date% %time%] Listo.
