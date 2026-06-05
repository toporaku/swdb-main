@echo off
rem =============================================================================
rem SCRIPT ORQUESTADOR SWDB 2026 - start.bat (Windows)
rem Idioma: Español (México)
rem Descripción: Inicia los 9 microservicios. Utiliza Python si está disponible
rem              para mayor robustez; en su defecto, abre ventanas secundarias.
rem =============================================================================

title Orquestador de Servicios (SWDB 2026)
echo ==========================================================
echo     Iniciando Orquestador de Servicios (SWDB 2026)       
echo ==========================================================

rem 1. Verificar si Python está en el PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo -^> Detectado Python. Iniciando modulo de orquestacion run_services.py...
    python run_services.py
    goto end
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo -^> Detectado Python 3. Iniciando modulo de orquestacion run_services.py...
    python3 run_services.py
    goto end
)

echo ⚠️  Advertencia: Python no esta instalado en este sistema Windows.
echo Se iniciaran los microservicios abriendo multiples ventanas de comandos.
echo Por favor, cierre las ventanas individuales para detener los servicios.
pause

mkdir logs >nul 2>&1

echo Iniciando config-server...
start "Config Server - SWDB" /D "..\swdb-config-server" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\config-server.log 2>&1"
timeout /t 15

echo Iniciando registry-service...
start "Registry Service - SWDB" /D "..\swdb-registry-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\registry-service.log 2>&1"
timeout /t 15

echo Iniciando gateway-service...
start "Gateway Service - SWDB" /D "..\swdb-gateway-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\gateway-service.log 2>&1"
timeout /t 5

echo Iniciando admin-service...
start "Admin Service - SWDB" /D "..\swdb-admin-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\admin-service.log 2>&1"
timeout /t 5

echo Iniciando auth-service...
start "Auth Service - SWDB" /D "..\swdb-auth-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\auth-service.log 2>&1"
timeout /t 5

echo Iniciando product-service...
start "Product Service - SWDB" /D "..\swdb-product-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\product-service.log 2>&1"
timeout /t 5

echo Iniciando cart-service...
start "Cart Service - SWDB" /D "..\swdb-cart-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\cart-service.log 2>&1"
timeout /t 5

echo Iniciando invoice-service...
start "Invoice Service - SWDB" /D "..\swdb-invoice-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\invoice-service.log 2>&1"
timeout /t 5

echo Iniciando customer-service...
start "Customer Service - SWDB" /D "..\swdb-customer-service" cmd /c "mvn spring-boot:run > ..\swdb-main\logs\customer-service.log 2>&1"
timeout /t 5

echo ==========================================================
echo Todos los servicios han sido lanzados en ventanas separadas.
echo ==========================================================

:end
pause
