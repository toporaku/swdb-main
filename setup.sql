-- =============================================================================
-- SCRIPT DE CONFIGURACIÓN DE BASE DE DATOS - SWDB 2026
-- Idioma: Español (México)
-- Descripción: Este script crea las bases de datos necesarias para todos los 
--              microservicios y configura el usuario administrador 'swdb_user' 
--              con los permisos correspondientes.
-- =============================================================================

-- 1. Eliminar bases de datos existentes si ya existen para evitar conflictos
DROP DATABASE IF EXISTS SWDB2026;
DROP DATABASE IF EXISTS db_cart;
DROP DATABASE IF EXISTS db_auth;
DROP DATABASE IF EXISTS db_invoice;
DROP DATABASE IF EXISTS dwb_customer_service;

-- 2. Creación de las bases de datos para cada microservicio
CREATE DATABASE SWDB2026 CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
CREATE DATABASE db_cart CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
CREATE DATABASE db_auth CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
CREATE DATABASE db_invoice CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
CREATE DATABASE dwb_customer_service CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;

-- 3. Configuración de seguridad: Crear el usuario exclusivo para la aplicación
-- Nota: Si el usuario ya existe, se elimina primero para asegurar su recreación limpia.
DROP USER IF EXISTS 'swdb_user'@'localhost';
DROP USER IF EXISTS 'swdb_user'@'%';

CREATE USER 'swdb_user'@'localhost' IDENTIFIED BY 'Swdb_2026_Project!';
CREATE USER 'swdb_user'@'%' IDENTIFIED BY 'Swdb_2026_Project!';

-- 4. Asignación de permisos al usuario sobre todas las bases de datos del sistema
GRANT ALL PRIVILEGES ON SWDB2026.* TO 'swdb_user'@'localhost';
GRANT ALL PRIVILEGES ON SWDB2026.* TO 'swdb_user'@'%';

GRANT ALL PRIVILEGES ON db_cart.* TO 'swdb_user'@'localhost';
GRANT ALL PRIVILEGES ON db_cart.* TO 'swdb_user'@'%';

GRANT ALL PRIVILEGES ON db_auth.* TO 'swdb_user'@'localhost';
GRANT ALL PRIVILEGES ON db_auth.* TO 'swdb_user'@'%';

GRANT ALL PRIVILEGES ON db_invoice.* TO 'swdb_user'@'localhost';
GRANT ALL PRIVILEGES ON db_invoice.* TO 'swdb_user'@'%';

GRANT ALL PRIVILEGES ON dwb_customer_service.* TO 'swdb_user'@'localhost';
GRANT ALL PRIVILEGES ON dwb_customer_service.* TO 'swdb_user'@'%';

-- Aplicar los cambios de privilegios
FLUSH PRIVILEGES;

-- =============================================================================
-- FIN DEL SCRIPT DE CONFIGURACIÓN
-- =============================================================================
