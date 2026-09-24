@echo off
REM ── Actualización diaria del dashboard ────────────────────────────────────
REM Se ejecuta desde la carpeta del proyecto (proyectos\reportes_operativos), padre de este .bat

cd /d "%~dp0.."

echo [%date% %time%] Generando datos metaliados...
python SCRIPTS_PYTHON\generar_seguimiento_metaliados.py >> seguimiento_web\actualizar.log 2>&1

echo [%date% %time%] Generando cosechas por region...
python SCRIPTS_PYTHON\generar_cosechas.py >> seguimiento_web\actualizar.log 2>&1

echo [%date% %time%] Subiendo a GitHub...
cd seguimiento_web
git add data\seguimiento_metaliados.csv data\seguimiento_cosechas.csv
git add data\cosechas_general.csv data\cosechas_mensual.csv
git add pages\cosechas.py app.py requirements.txt
git commit -m "Actualización automática %date%" >> actualizar.log 2>&1
git push >> actualizar.log 2>&1

echo [%date% %time%] Listo.
