import subprocess
import time
import sys
import os
import signal

SERVICES = [
    {"name": "config-server", "dir": "config-server", "port": 8888},
    {"name": "registry-service", "dir": "registry-service", "port": 8761},
    {"name": "gateway-service", "dir": "gateway-service", "port": 8080},
    {"name": "admin-service", "dir": "admin-service", "port": 9090},
    {"name": "auth-service", "dir": "auth-service", "port": 8082},
    {"name": "product-service", "dir": "product-service", "port": 8083},
    {"name": "cart-service", "dir": "cart-service", "port": 8085},
    {"name": "invoice-service", "dir": "invoice-service", "port": 8084},
    {"name": "customer-service", "dir": "customer-service", "port": 8081}
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
    print("\n\nShutting down all microservices...")
    for p, name in processes:
        print(f"Stopping {name}...")
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    print("All services stopped.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    os.makedirs("logs", exist_ok=True)
    
    print("Pre-flight port cleanup...")
    for svc in SERVICES:
        if check_port_in_use(svc["port"]):
            print(f"Port {svc['port']} is already in use by {svc['name']}. Cleaning up...")
            kill_port_owner(svc["port"])
            
    print("\nStarting microservices...")
    for svc in SERVICES:
        name = svc["name"]
        directory = svc["dir"]
        port = svc["port"]
        
        print(f"Starting {name} on port {port}...")
        log_file = open(f"logs/{name}.log", "w")
        p = subprocess.Popen(["mvn", "spring-boot:run"], cwd=directory, stdout=log_file, stderr=log_file)
        processes.append((p, name))
        
        # Wait until port is open
        retries = 35
        success = False
        while retries > 0:
            if p.poll() is not None:
                print(f"ERROR: {name} process terminated early. Check logs/{name}.log")
                cleanup()
                
            if check_port_in_use(port):
                print(f"-> {name} is UP on port {port}.")
                success = True
                break
            time.sleep(2)
            retries -= 1
            
        if not success:
            print(f"ERROR: {name} failed to start on port {port} within timeout. Check logs/{name}.log")
            cleanup()
            
    print("\n==========================================================")
    print("ALL SERVICES ACTIVE AND DEPLOYED!")
    print("Press Ctrl+C to stop all services and terminate processes.")
    print("==========================================================")
    
    # Idle loop to keep running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
