# -*- coding: utf-8 -*-
"""
SCRIPT DE POBLACIÓN DE DATOS DE PRUEBA (SWDB 2026)
Idioma: Español (México)
Descripción: Este script realiza peticiones HTTP a través de API Gateway (puerto 8080)
             para registrar datos iniciales (Regiones, Categorías, Productos y Clientes)
             en el sistema utilizando las credenciales predeterminadas.
"""

import urllib.request
import urllib.error
import json
import time
import base64
import sys

GATEWAY_URL = "http://localhost:8080"

def realizar_peticion(url, metodo="GET", cabeceras=None, datos=None):
    if cabeceras is None:
        cabeceras = {}
    if datos is not None:
        if isinstance(datos, (dict, list)):
            datos = json.dumps(datos).encode('utf-8')
            cabeceras['Content-Type'] = 'application/json'
        elif isinstance(datos, str):
            datos = datos.encode('utf-8')

    req = urllib.request.Request(url, data=datos, headers=cabeceras, method=metodo)
    try:
        with urllib.request.urlopen(req) as respuesta:
            status = respuesta.getcode()
            cuerpo = respuesta.read().decode('utf-8')
            return status, cuerpo
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error de conexión a {url}: {e.reason}")
        return 0, str(e.reason)

def obtener_id_usuario_de_jwt(token):
    # Decodificar el JWT para extraer el ID de usuario
    partes = token.split(".")
    if len(partes) < 2:
        return None
    carga_util_b64 = partes[1]
    # Ajustar padding de base64
    carga_util_b64 += "=" * ((4 - len(carga_util_b64) % 4) % 4)
    payload_str = base64.urlsafe_b64decode(carga_util_b64).decode("utf-8")
    payload = json.loads(payload_str)
    return payload.get("id")

def main():
    print("=== Iniciando Población de Datos de Prueba ===")
    
    # 1. Iniciar sesión como Administrador por defecto
    print("\n[1] Iniciando sesión como Administrador...")
    credenciales_admin = {
        "username": "admin",
        "password": "Password123!"
    }
    status, cuerpo = realizar_peticion(
        f"{GATEWAY_URL}/auth-service/login", 
        "POST", 
        datos=credenciales_admin
    )
    
    if status != 200:
        print("Error: No se pudo autenticar al Administrador predeterminado.")
        print(f"Status: {status}, Respuesta: {cuerpo}")
        sys.exit(1)
        
    token_admin = json.loads(cuerpo)["token"]
    cabeceras_admin = {"Authorization": f"Bearer {token_admin}"}
    print("-> Autenticación de Administrador exitosa.")

    # 2. Registrar Regiones en customer-service
    print("\n[2] Insertando Regiones de prueba...")
    regiones = [
        {"region": "Norte"},
        {"region": "Sur"},
        {"region": "Centro"},
        {"region": "Este"},
        {"region": "Oeste"}
    ]
    for reg in regiones:
        status, cuerpo = realizar_peticion(
            f"{GATEWAY_URL}/customer-service/region",
            "POST",
            cabeceras=cabeceras_admin,
            datos=reg
        )
        print(f"Insertando region '{reg['region']}': Status {status}")

    # 3. Registrar Categorías en product-service
    print("\n[3] Insertando Categorías de productos...")
    categorias = [
        {"category": "Electrónica", "tag": "ELEC"},
        {"category": "Hogar", "tag": "HOGR"},
        {"category": "Libros", "tag": "LIBR"}
    ]
    for cat in categorias:
        status, cuerpo = realizar_peticion(
            f"{GATEWAY_URL}/product-service/category",
            "POST",
            cabeceras=cabeceras_admin,
            datos=cat
        )
        print(f"Insertando categoría '{cat['category']}': Status {status}")

    # Activar las categorías creadas (por defecto pueden requerir activación)
    # Las categorías creadas toman IDs secuenciales (1, 2, 3)
    for i in range(1, 4):
        realizar_peticion(
            f"{GATEWAY_URL}/product-service/category/{i}/enable",
            "PATCH",
            cabeceras=cabeceras_admin
        )

    # 4. Registrar Productos en product-service
    print("\n[4] Insertando Productos de prueba...")
    productos = [
        {
            "gtin": "1234567890123",
            "product": "Laptop Pro 15",
            "description": "Laptop de alto rendimiento para desarrollo y diseño.",
            "price": 24999.00,
            "stock": 100,
            "category_id": 1
        },
        {
            "gtin": "9876543210987",
            "product": "Cafetera Espresso",
            "description": "Cafetera automática de acero inoxidable.",
            "price": 3499.50,
            "stock": 50,
            "category_id": 2
        },
        {
            "gtin": "1112223334445",
            "product": "Libro de Microservicios",
            "description": "Guía completa para construir microservicios con Spring Boot.",
            "price": 599.00,
            "stock": 200,
            "category_id": 3
        }
    ]
    for prod in productos:
        status, cuerpo = realizar_peticion(
            f"{GATEWAY_URL}/product-service/product",
            "POST",
            cabeceras=cabeceras_admin,
            datos=prod
        )
        print(f"Insertando producto '{prod['product']}': Status {status}")

    # 5. Registrar un Usuario Cliente estándar
    print("\n[5] Registrando Usuario Cliente estándar...")
    cliente_auth = {
        "username": "juan_perez",
        "email": "juan.perez@mail.com",
        "password": "Password123!",
        "name": "Juan",
        "lastName": "Pérez",
        "phoneNumber": "5551234567",
        "roles": ["User"]
    }
    status, cuerpo = realizar_peticion(
        f"{GATEWAY_URL}/auth-service/user",
        "POST",
        datos=cliente_auth
    )
    if status == 200 or "registrado" in cuerpo.lower() or "existe" in cuerpo.lower():
        print("-> Usuario cliente registrado correctamente o ya existente.")
    else:
        print(f"Error al registrar usuario cliente: Status {status}, Respuesta: {cuerpo}")
        sys.exit(1)

    # Iniciar sesión como Cliente para obtener su JWT y ID de usuario
    print("\n[6] Iniciando sesión como Cliente...")
    status, cuerpo = realizar_peticion(
        f"{GATEWAY_URL}/auth-service/login",
        "POST",
        datos={"username": "juan_perez", "password": "Password123!"}
    )
    if status != 200:
        print("Error al iniciar sesión como cliente.")
        sys.exit(1)
        
    token_cliente = json.loads(cuerpo)["token"]
    id_usuario_cliente = obtener_id_usuario_de_jwt(token_cliente)
    cabeceras_cliente = {"Authorization": f"Bearer {token_cliente}"}
    
    # 6. Crear el perfil de Cliente en customer-service
    print(f"\n[7] Registrando Perfil de Cliente (User ID: {id_usuario_cliente})...")
    perfil_cliente = {
        "name": "Juan",
        "surname": "Pérez",
        "rfc": "PERJ800101XYZ",
        "mail": "juan.perez@mail.com",
        "phone_number": "5551234567",
        "address": "Av. Paseo de la Reforma 123, CDMX",
        "user_id": id_usuario_cliente,
        "region_id": 3 # Centro
    }
    status, cuerpo = realizar_peticion(
        f"{GATEWAY_URL}/customer-service/customer",
        "POST",
        cabeceras=cabeceras_cliente,
        datos=perfil_cliente
    )
    print(f"Registrando perfil de cliente: Status {status}, Respuesta: {cuerpo}")

    print("\n=== Población de Datos Finalizada con Éxito ===")

if __name__ == "__main__":
    main()
