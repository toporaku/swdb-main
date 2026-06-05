import subprocess
import time
import urllib.request
import urllib.error
import json
import sys
import os
import signal

SERVICES = [
    {"name": "config-server", "dir": "../swdb-config-server", "port": 8888, "url": "http://localhost:8888/actuator/health"},
    {"name": "registry-service", "dir": "../swdb-registry-service", "port": 8761, "url": "http://localhost:8761/eureka/apps"},
    {"name": "gateway-service", "dir": "../swdb-gateway-service", "port": 8080, "url": "http://localhost:8080/actuator/health"},
    {"name": "admin-service", "dir": "../swdb-admin-service", "port": 9090, "url": "http://localhost:9090/actuator/health"},
    {"name": "auth-service", "dir": "../swdb-auth-service", "port": 8082, "url": "http://localhost:8082/actuator/health"},
    {"name": "product-service", "dir": "../swdb-product-service", "port": 8083, "url": "http://localhost:8083/actuator/health"},
    {"name": "cart-service", "dir": "../swdb-cart-service", "port": 8085, "url": "http://localhost:8085/actuator/health"},
    {"name": "invoice-service", "dir": "../swdb-invoice-service", "port": 8084, "url": "http://localhost:8084/actuator/health"},
    {"name": "customer-service", "dir": "../swdb-customer-service", "port": 8081, "url": "http://localhost:8081/actuator/health"}
]

processes = []

def make_request(url, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    if data is not None:
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif isinstance(data, str):
            data = data.encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            return status_code, response_body, response.info()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8'), e.info()
    except urllib.error.URLError as e:
        return 0, str(e.reason), {}

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

def cleanup():
    print("\nShutting down all microservices...")
    for p, name in processes:
        print(f"Stopping {name}...")
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    print("Cleanup completed.")

def main():
    os.makedirs("logs", exist_ok=True)
    
    # 0. Database cleanup
    print("Cleaning up test database records...")
    subprocess.run([
        "mysql", "-u", "swdb_user", "-pSwdb_2026_Project!", "-e", 
        "DELETE FROM db_auth.user_roles WHERE user_id IN (SELECT id FROM db_auth.user WHERE username='customer_e2e'); "
        "DELETE FROM db_auth.user WHERE username='customer_e2e'; "
        "DELETE FROM dwb_customer_service.customer_image WHERE customer_id IN (SELECT customer_id FROM dwb_customer_service.customer WHERE mail='customer_e2e@mail.com'); "
        "DELETE FROM dwb_customer_service.customer WHERE mail='customer_e2e@mail.com';"
    ], capture_output=True)
    
    # 1. Clean up existing processes on target ports
    print("Pre-flight port cleanup...")
    for svc in SERVICES:
        if check_port_in_use(svc["port"]):
            print(f"Port {svc['port']} is already in use by {svc['name']}. Cleaning up...")
            kill_port_owner(svc["port"])
            
    # 2. Start services sequentially
    print("\nStarting microservices...")
    for svc in SERVICES:
        name = svc["name"]
        directory = svc["dir"]
        port = svc["port"]
        url = svc["url"]
        
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
                sys.exit(1)
                
            if check_port_in_use(port):
                print(f"-> {name} is UP on port {port}.")
                success = True
                break
            time.sleep(2)
            retries -= 1
            
        if not success:
            print(f"ERROR: {name} failed to start on port {port} within timeout. Check logs/{name}.log")
            cleanup()
            sys.exit(1)
            
    print("\nAll microservices started and registered. Waiting 35 seconds for Eureka discovery propagation...")
    time.sleep(35)

    # 3. Run E2E Integration Workflow
    print("\nRunning E2E integration workflow tests...")
    gateway_url = "http://localhost:8080"
    
    try:
        # Step A: Register customer
        print("\n[Step A] Registering new user...")
        reg_payload = {
            "username": "customer_e2e",
            "email": "customer_e2e@mail.com",
            "password": "Password123!",
            "name": "Customer",
            "lastName": "E2E",
            "phoneNumber": "12345678901",
            "roles": ["User"]
        }
        status, body, _ = make_request(f"{gateway_url}/auth-service/user", "POST", data=reg_payload)
        print(f"Status: {status}, Response: {body}")
        if status != 200:
            raise Exception("User registration failed")

        # Step B: Login
        print("\n[Step B] Logging in to retrieve JWT...")
        login_payload = {
            "username": "customer_e2e",
            "password": "Password123!"
        }
        status, body, _ = make_request(f"{gateway_url}/auth-service/login", "POST", data=login_payload)
        print(f"Status: {status}, Response: {body}")
        if status != 200:
            raise Exception("Login failed")
        
        token = json.loads(body)["token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Dynamically decode JWT payload to get user ID
        import base64
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
        actual_user_id = payload_json.get("id", 2)

        # Step C: Register Customer profile in customer-service
        print("\n[Step C] Registering customer profile...")
        cust_payload = {
            "name": "Customer",
            "surname": "Eee",
            "rfc": "CUST900101XYZ",
            "mail": "customer_e2e@mail.com",
            "phone_number": "12345678901",
            "address": "123 E2E Street",
            "user_id": actual_user_id,
            "region_id": 1 # North Region active region
        }
        status, body, _ = make_request(f"{gateway_url}/customer-service/customer", "POST", headers=auth_headers, data=cust_payload)
        print(f"Status: {status}, Response: {body}")
        if status != 200:
            raise Exception("Customer profile registration failed")

        # Step D: Get Product details
        print("\n[Step D] Fetching product by GTIN to check initial stock...")
        status, body, _ = make_request(f"{gateway_url}/product-service/product/gtin/1234567890123", headers=auth_headers)
        print(f"Status: {status}, Response: {body}")
        if status != 200:
            raise Exception("Product lookup failed")
        
        prod_data = json.loads(body)
        initial_stock = prod_data["stock"]
        print(f"Initial Product Stock: {initial_stock}")

        # Step E: Add Product to Cart
        print("\n[Step E] Adding product to cart...")
        cart_payload = {
            "cartId": actual_user_id,
            "gtin": "1234567890123",
            "quantity": 2
        }
        status, body, _ = make_request(f"{gateway_url}/cart-service/cart-item", "POST", headers=auth_headers, data=cart_payload)
        print(f"Status: {status}, Response: {body}")
        if status != 201:
            raise Exception("Add to cart failed")

        # Step F: Checkout via invoice-service
        print("\n[Step F] Checking out via invoice-service...")
        checkout_payload = {
            "shipping_address": "123 E2E Street",
            "payment_method": "Credit Card",
            "coupon_code": "SAVE10"
        }
        status, body, _ = make_request(f"{gateway_url}/invoice-service/invoice", "POST", headers=auth_headers, data=checkout_payload)
        print(f"Status: {status}, Response: {body}")
        if status != 200:
            raise Exception("Checkout failed")

        # Step G: Verify Cart is cleared
        print("\n[Step G] Verifying cart is cleared...")
        status, body, _ = make_request(f"{gateway_url}/cart-service/cart-item/user/{actual_user_id}", "GET", headers=auth_headers)
        print(f"Status: {status}, Response: {body}")
        cart_items = json.loads(body)
        if len(cart_items) != 0:
            raise Exception("Cart was not cleared after checkout")
        print("-> Success: Cart is empty.")

        # Step H: Verify Stock is decremented
        print("\n[Step H] Verifying product stock is decremented...")
        status, body, _ = make_request(f"{gateway_url}/product-service/product/gtin/1234567890123", headers=auth_headers)
        print(f"Status: {status}, Response: {body}")
        prod_data = json.loads(body)
        final_stock = prod_data["stock"]
        print(f"Final Product Stock: {final_stock}")
        if final_stock != (initial_stock - 2):
            raise Exception("Product stock was not correctly decremented")
        print("-> Success: Stock decremented by 2.")

        print("\n==============================================")
        print("E2E INTEGRATION TEST RESULT: SUCCESS (ALL PASSED)")
        print("==============================================")

    except Exception as e:
        print(f"\nERROR DURING INTEGRATION TESTS: {str(e)}")
        cleanup()
        sys.exit(1)
        
    cleanup()

if __name__ == "__main__":
    main()
