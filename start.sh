#!/bin/bash
# =============================================================================
# SCRIPT ORQUESTADOR SWDB 2026 - start.sh
# Idioma: Español (México)
# Descripción: Inicia de forma secuencial y ordenada los 9 microservicios del 
#              sistema. Utiliza el módulo de Python si está disponible; de lo 
#              contrario, lanza los procesos en segundo plano usando bash.
# =============================================================================

# Obtener la ruta absoluta del directorio del script
DIR_ACTUAL="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR_ACTUAL"

echo "=========================================================="
echo "    Iniciando Orquestador de Servicios (SWDB 2026)        "
echo "=========================================================="

# 1. Verificar si Python 3 está disponible para usar la orquestación inteligente
if command -v python3 &>/dev/null; then
    echo "-> Detectado Python 3. Iniciando módulo de orquestación run_services.py..."
    python3 run_services.py
    exit 0
fi

echo "⚠️  Advertencia: Python 3 no está instalado. Iniciando modo de compatibilidad bash..."
echo "Nota: Se iniciarán los microservicios en segundo plano. Los logs se guardarán en la carpeta 'logs/'."

mkdir -p logs

SERVICIOS=(
    "config-server:8888:../swdb-config-server"
    "registry-service:8761:../swdb-registry-service"
    "gateway-service:8080:../swdb-gateway-service"
    "admin-service:9090:../swdb-admin-service"
    "auth-service:8082:../swdb-auth-service"
    "product-service:8083:../swdb-product-service"
    "cart-service:8085:../swdb-cart-service"
    "invoice-service:8084:../swdb-invoice-service"
    "customer-service:8081:../swdb-customer-service"
)

PIDS=()

detener_servicios() {
    echo -e "\n\nDeteniendo todos los servicios en segundo plano..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Deteniendo proceso PID $pid..."
            kill "$pid" 2>/dev/null
        fi
    done
    echo "Todos los servicios han sido detenidos."
    exit 0
}

# Capturar Ctrl+C (SIGINT) y SIGTERM para apagar todo limpiamente
trap detener_servicios SIGINT SIGTERM

for item in "${SERVICIOS[@]}"; do
    IFS=":" read -r name port path <<< "$item"
    
    # Limpiar puertos si ya están en uso (en macOS / Linux)
    if lsof -t -i:"$port" &>/dev/null; then
        echo "El puerto $port ya está en uso. Limpiando propietario..."
        kill -9 $(lsof -t -i:"$port") 2>/dev/null
        sleep 1
    fi
    
    echo "Iniciando $name en puerto $port (Directorio: $path)..."
    cd "$path"
    mvn spring-boot:run > "$DIR_ACTUAL/logs/$name.log" 2>&1 &
    PID=$!
    PIDS+=("$PID")
    cd "$DIR_ACTUAL"
    
    # Espera básica para el inicio secuencial
    if [ "$name" == "config-server" ] || [ "$name" == "registry-service" ]; then
        echo "Esperando 15 segundos para inicializar infraestructura crítica..."
        sleep 15
    else
        sleep 5
    fi
done

echo "=========================================================="
echo "¡TODOS LOS SERVICIOS HAN SIDO LANZADOS EN SEGUNDO PLANO!"
echo "Revisa la carpeta 'logs/' para ver las salidas individuales."
echo "Presiona [Ctrl+C] en esta terminal para apagarlos."
echo "=========================================================="

while true; do
    sleep 1
done
