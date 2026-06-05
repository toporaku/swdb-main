# Customer Service LLD (Low-Level Design)

## Purpose
The Customer Service (`customer-service`) manages regions, customer profiles, and customer profile images. It acts as a standalone microservice within the Spring Cloud ecosystem, registering with Eureka and fetching its configuration from the Config Server.

## Scope
- Centralized configuration via Config Server (`customer-service.properties`).
- Service discovery registration with Eureka as `customer-service`.
- Catalog administration for regions (Region CRUD).
- Customer profile administration (Customer CRUD).
- Customer profile image management (Upload / Status tracking).
- JWT Authentication integration using a shared secret and authority checks (`ADMIN`, `CUSTOMER`).

## Component Design

### 1. Database Schema (`dwb_customer_service`)
This service uses its own MySQL database instance.

```sql
CREATE DATABASE IF NOT EXISTS dwb_customer_service;
USE dwb_customer_service;

CREATE TABLE region (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    tag VARCHAR(10) NOT NULL,
    status INT NOT NULL DEFAULT 1
);

CREATE TABLE customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    rfc VARCHAR(13) NOT NULL,
    mail VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    address VARCHAR(255) NOT NULL,
    user_id INT NOT NULL,
    region_id INT NOT NULL,
    status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (region_id) REFERENCES region(region_id)
);

CREATE TABLE customer_image (
    customer_image_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    image TEXT NOT NULL,
    status INT NOT NULL DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);
```

### 2. Java Package & Class Structure
Root Package: `com.customer_service`

- **Config**:
  - `config.security.SecurityConfig`: Controls route authorization based on Roles (Authorities).
  - `config.security.CorsConfig`: Configures CORS policy.
  - `config.jwt.JwtAuthFilter`: Extracts JWT, validates claims, sets authentication context with `CUSTOMER` or `ADMIN` authority.
  - `config.jwt.JwtUtil`: Handles JWT decoding.
  - `config.openapi.OpenApiConfig`: Swagger OpenAPI configurations.
- **Entity**:
  - `api.entity.Region`: Matches database table `region`.
  - `api.entity.Customer`: Matches database table `customer`.
  - `api.entity.CustomerImage`: Matches database table `customer_image`.
- **DTOs**:
  - `api.dto.DtoRegionIn`: Input payload for creating/updating Region.
  - `api.dto.DtoCustomerIn`: Input payload for creating/updating Customer.
  - `api.dto.DtoCustomerOut`: Complete detail payload for Customer (contains region entity).
  - `api.dto.DtoCustomerListOut`: List item payload for Customer.
  - `api.dto.DtoCustomerImageIn`: Input payload for customer image upload (base64).
- **Controller**:
  - `api.controller.CtrlRegion`: Exposes endpoints for region management.
  - `api.controller.CtrlCustomer`: Exposes endpoints for customer profile management.
  - `api.controller.CtrlCustomerImage`: Exposes endpoint for customer image management.
- **Service**:
  - `api.service.SvcRegion` & `SvcRegionImp`: Implements Region catalog CRUD logic.
  - `api.service.SvcCustomer` & `SvcCustomerImp`: Implements Customer profile CRUD and validation logic.
  - `api.service.SvcCustomerImage` & `SvcCustomerImageImp`: Implements image upload/saving logic.
- **Repository**:
  - `api.repository.RepoRegion`: JpaRepository for Region.
  - `api.repository.RepoCustomer`: JpaRepository for Customer.
  - `api.repository.RepoCustomerImage`: JpaRepository for CustomerImage.
- **Exception**:
  - `exception.ApiException` & `exception.DBAccessException` & `exception.RestExceptionHandler`.

### 3. Key API Endpoints & Authorization Rules
| Method | Path | Required Authority | Description |
|--------|------|--------------------|-------------|
| GET | `/region` | `permitAll` | Returns all regions |
| GET | `/region/active` | `permitAll` | Returns active regions (status = 1) |
| POST | `/region` | `ADMIN` | Creates a new region |
| PUT | `/region/{id}` | `ADMIN` | Updates an existing region |
| PATCH | `/region/{id}/enable` | `ADMIN` | Enables a region (status = 1) |
| PATCH | `/region/{id}/disable` | `ADMIN` | Disables a region (status = 0) |
| GET | `/customer` | `ADMIN` | Lists all customer profiles |
| GET | `/customer/{id}` | `ADMIN` or `CUSTOMER` | Returns customer details by ID |
| POST | `/customer` | `ADMIN` or `CUSTOMER` | Registers a new customer profile |
| PUT | `/customer/{id}` | `ADMIN` or `CUSTOMER` | Updates an existing customer profile |
| PATCH | `/customer/{id}/enable` | `ADMIN` | Enables a customer profile |
| PATCH | `/customer/{id}/disable` | `ADMIN` | Disables a customer profile |
| POST | `/customer-image` | `ADMIN` or `CUSTOMER` | Uploads a customer profile image |

### 4. Decisions & Alternatives
| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|-------------------------|-----------|
| Port & Db | Port 8081, Db `dwb_customer_service` | Shared Auth Db | Promotes microservice data isolation and matches the reference config setup. |
| Security Strategy | Role validation using authorities (ADMIN, CUSTOMER) | Method-level security annotations | Consistent with the reference configuration code structure. |
