import subprocess
import time
import sys
import os
import signal

SERVICES = [
    {"name": "config-server", "dir": "../swdb-config-server", "port": 8888},
    {"name": "registry-service", "dir": "../swdb-registry-service", "port": 8761},
    {"name": "gateway-service", "dir": "../swdb-gateway-service", "port": 8080},
    {"name": "admin-service", "dir": "../swdb-admin-service", "port": 9090},
    {"name": "auth-service", "dir": "../swdb-auth-service", "port": 8082},
    {"name": "product-service", "dir": "../swdb-product-service", "port": 8083},
    {"name": "cart-service", "dir": "../swdb-cart-service", "port": 8085},
    {"name": "invoice-service", "dir": "../swdb-invoice-service", "port": 8084},
    {"name": "customer-service", "dir": "../swdb-customer-service", "port": 8081}
]

processes = []

def check_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port_owner(port):
    try:
        output = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode().strip()
        if output:
            for pid in output.split('\n'):
                print(f"Killing process {pid} using port {port}")
                os.kill(int(pid), signal.SIGKILL)
            time.sleep(1)
    except subprocess.CalledProcessError:
        pass

def cleanup(sig=None, frame=None):
    print("\n\nApagando todos los microservicios...")
    for p, name in processes:
        print(f"Deteniendo {name}...")
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    print("Todos los servicios detenidos.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    os.makedirs("logs", exist_ok=True)
    
    print("Limpieza previa de puertos...")
    for svc in SERVICES:
        if check_port_in_use(svc["port"]):
            print(f"El puerto {svc['port']} ya está en uso por {svc['name']}. Limpiando...")
            kill_port_owner(svc["port"])
            
    print("\nIniciando microservicios...")
    for svc in SERVICES:
        name = svc["name"]
        directory = svc["dir"]
        port = svc["port"]
        
        print(f"Iniciando {name} en el puerto {port}...")
        log_file = open(f"logs/{name}.log", "w")
        p = subprocess.Popen(["mvn", "spring-boot:run"], cwd=directory, stdout=log_file, stderr=log_file)
        processes.append((p, name))
        
        # Wait until port is open
        retries = 35
        success = False
        while retries > 0:
            if p.poll() is not None:
                print(f"ERROR: El proceso {name} terminó inesperadamente. Revisa logs/{name}.log")
                cleanup()
                
            if check_port_in_use(port):
                print(f"-> {name} está ACTIVO en el puerto {port}.")
                success = True
                break
            time.sleep(2)
            retries -= 1
            
        if not success:
            print(f"ERROR: {name} falló al iniciar en el puerto {port} dentro del tiempo límite. Revisa logs/{name}.log")
            cleanup()
            
    print("\n==========================================================")
    print("¡TODOS LOS SERVICIOS ESTÁN ACTIVOS Y DESPLEGADOS!")
    print("Presiona Ctrl+C para detener todos los servicios de forma segura.")
    print("==========================================================")
    
    # Idle loop to keep running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
