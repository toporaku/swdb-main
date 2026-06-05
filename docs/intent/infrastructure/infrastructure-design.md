---
parent: high-level-design
prefix: INFRA
---

# Infrastructure Services

## Context and Design Philosophy

The infrastructure segment provides the foundational services that all business services depend on: centralized configuration, service discovery, API routing, and operational monitoring. None of these services contain business logic or own a database. They exist to make the business services (auth, product, cart, invoice, customer) discoverable, configurable, and accessible through a single external entry point.

All four infrastructure services follow the instructor's reference implementations closely. Each is a minimal Spring Boot application with a single enabling annotation (`@EnableConfigServer`, `@EnableEurekaServer`, `@EnableAdminServer`) and externalized configuration. The reference code uses Spring Boot 4.0.6 and Spring Cloud 2025.1.1; config-service's reference POM has 4.0.5, which we standardize to 4.0.6.

Infrastructure services must start before any business service, in a fixed order: Config Server → Registry → Gateway → Admin.

## Config Server

### Purpose

Externalizes configuration for all services into a Git-backed repository (`config-data/`). Each service fetches its configuration on startup by matching its `spring.application.name` to a file in the repository (e.g., `registry-service.yaml`, `gateway-service.yaml`).

### Implementation

- **Main class**: `@SpringBootApplication` + `@EnableConfigServer`
- **Package**: `com.config_service`
- **Port**: 8888 (hardcoded in `application.properties`, not pulled from config-data since this is the config source itself)
- **Git URI**: Points to the local `config-data/` repository. The reference uses `https://github.com/ivansaavedrapm/config-data_20262.git`; we use a local path or a forked GitHub repo.
- **Default label**: `master`

### Key dependency

```xml
<artifactId>spring-cloud-config-server</artifactId>
```

### Config Server does NOT register with Eureka

Config Server is the first service to start and has no Eureka dependency. Other services connect to it via hardcoded `http://localhost:8888`.

## Config-Data Repository

### Purpose

A Git repository holding per-service configuration files. The Config Server reads from this repository at runtime.

### File naming convention

Each file is named `{spring.application.name}.{yaml|properties}`. The file name must match the service's `spring.application.name` exactly.

### Existing files (from reference)

| File | Format | Service |
|------|--------|---------|
| `registry-service.yaml` | YAML | Registry (Eureka) |
| `gateway-service.yaml` | YAML | Gateway |
| `admin-service.yaml` | YAML | Admin |
| `customer-service.properties` | Properties | Customer |

### Files to create

| File | Format | Service | Key content |
|------|--------|---------|-------------|
| `auth.properties` | Properties | Auth | datasource (DWB2026_2), JWT secret, Eureka registration, Actuator endpoints |
| `product.properties` | Properties | Product | datasource (SWDB2026), JWT secret, Eureka registration, Actuator endpoints |
| `cart-service.properties` | Properties | Cart | datasource (db_cart), JWT secret, Eureka registration, Actuator endpoints |
| `invoice.properties` | Properties | Invoice | datasource (db_invoice), JWT secret, Eureka registration, Actuator endpoints |

### Config-data naming consistency rule

The Eureka `lb://` URI in gateway routes uses the uppercased `spring.application.name`. The gateway config-data file must use Eureka names that match what each service registers as. Current mapping:

| Service | `spring.application.name` | Eureka Name (uppercase) | Gateway `lb://` URI |
|---------|--------------------------|------------------------|---------------------|
| Auth | `auth` | `AUTH` | `lb://AUTH` |
| Product | `product` | `PRODUCT` | `lb://PRODUCT` |
| Cart | `cart-service` | `CART-SERVICE` | `lb://CART-SERVICE` |
| Invoice | `invoice` | `INVOICE` | `lb://INVOICE` |
| Customer | `customer-service` | `CUSTOMER-SERVICE` | `lb://CUSTOMER-SERVICE` |

## Registry Service (Eureka)

### Purpose

Netflix Eureka Server for service discovery. All business services and the gateway register here. Services use Eureka to resolve logical service names (e.g., `PRODUCT`) to physical `host:port` addresses for inter-service REST calls.

### Implementation

- **Main class**: `@SpringBootApplication` + `@EnableEurekaServer`
- **Package**: `com.registry_service`
- **Port**: 8761 (from config-data)
- **Config client**: Connects to Config Server via `spring.config.import=optional:configserver:` + `spring.cloud.config.uri=http://localhost:8888`

### Self-registration disabled

The Eureka server does not register with itself:

```yaml
eureka:
  client:
    register-with-eureka: false
    fetch-registry: false
```

### Key dependencies

```xml
<artifactId>spring-cloud-starter-config</artifactId>
<artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
```

## Gateway Service

### Purpose

Spring Cloud Gateway (WebMVC variant) that routes external HTTP traffic to the appropriate business service via Eureka load balancing. The gateway is the single external entry point; clients never call business services directly.

### Implementation

- **Main class**: `@SpringBootApplication` (no special enabling annotation needed for Gateway MVC)
- **Package**: `com.gateway_service`
- **Port**: 8080 (from config-data)
- **Config client**: Same pattern as registry

### Route configuration (in config-data `gateway-service.yaml`)

Routes are defined under `spring.cloud.gateway.server.webmvc.routes`. Each route:
1. Matches an external path prefix (e.g., `/auth-service/**`)
2. Forwards to a Eureka-resolved URI (e.g., `lb://AUTH`)
3. Strips the service-name prefix with `StripPrefix=1`

This means `GET http://localhost:8080/product-service/product` becomes `GET http://PRODUCT:8083/product`.

### Complete route table

| Route ID | External Path | Target | StripPrefix |
|----------|--------------|--------|-------------|
| `auth-service` | `/auth-service/**` | `lb://AUTH` | 1 |
| `product-service` | `/product-service/**` | `lb://PRODUCT` | 1 |
| `cart-service` | `/cart-service/**` | `lb://CART-SERVICE` | 1 |
| `invoice-service` | `/invoice-service/**` | `lb://INVOICE` | 1 |
| `customer-service` | `/customer-service/**` | `lb://CUSTOMER-SERVICE` | 1 |

### Key dependencies

```xml
<artifactId>spring-cloud-starter-config</artifactId>
<artifactId>spring-cloud-starter-gateway-server-webmvc</artifactId>
<artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
```

## Admin Service

### Purpose

Spring Boot Admin Server dashboard for monitoring all registered services. Discovers services through Eureka and displays their health, metrics, loggers, and thread dumps.

### Implementation

- **Main class**: `@SpringBootApplication` + `@EnableAdminServer`
- **Package**: `com.admin_service`
- **Port**: 9090 (from config-data)
- **Config client**: Same pattern as registry and gateway

### Eureka-based discovery

The admin config-data enables service discovery so Admin auto-discovers monitored services:

```yaml
spring:
  boot:
    admin:
      discovery:
        enabled: true
```

### Key dependencies

```xml
<artifactId>spring-boot-starter-webmvc</artifactId>
<artifactId>spring-boot-admin-starter-server</artifactId>  <!-- de.codecentric, version 4.0.3 -->
<artifactId>spring-cloud-starter-config</artifactId>
<artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
```

### Admin Service name inconsistency

The reference config-data `admin-service.yaml` sets `spring.application.name: admin-server`, but the service directory and POM use `admin-service`. This is harmless — Eureka registers whatever name the config-data provides — but the application name in config-data (`admin-server`) must match the config file name (`admin-service.yaml`) for Config Server to serve the right file. The reference has a mismatch: the file is `admin-service.yaml` but declares `name: admin-server`. We will fix this by setting `spring.application.name: admin-service` in the config-data file so the name matches the filename.

## Business Service Integration Pattern

Every business service (auth, product, cart, invoice, customer) integrates with infrastructure using the same pattern:

### POM dependencies (added to each business service)

```xml
<artifactId>spring-cloud-starter-config</artifactId>
<artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
```

Plus the Spring Cloud BOM in `<dependencyManagement>`:

```xml
<groupId>org.springframework.cloud</groupId>
<artifactId>spring-cloud-dependencies</artifactId>
<version>2025.1.1</version>
<type>pom</type>
<scope>import</scope>
```

### application.yaml (minimal bootstrap in the service itself)

```yaml
spring:
  application:
    name: {service-name}
  profiles:
    active: dev
  config:
    import: "optional:configserver:"
  cloud:
    config:
      uri: http://localhost:8888
```

All other configuration (port, datasource, Eureka, Swagger, JWT, Actuator) moves to the config-data repository file.

### Actuator endpoints (in config-data, per service)

```properties
management.endpoints.web.exposure.include=health,info,metrics,loggers,threaddump,heapdump
management.endpoint.health.show-details=always
```

This exposes the endpoints needed for Spring Boot Admin monitoring.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Config-data format for new business services | `.properties` files | `.yaml` files | The reference uses `.properties` for customer-service (the only business service in config-data). Consistency with the existing file. YAML is used for infrastructure services. |
| Config Server Git source | Local `config-data/` directory (can be pushed to GitHub later) | Remote GitHub repo only | Local-first allows offline development and avoids Git authentication issues during development. |
| Admin service name fix | Set `spring.application.name: admin-service` in config-data | Keep `admin-server` and rename config file to `admin-server.yaml` | Changing the name inside the file is less disruptive than renaming the file, which would require updating any existing references. |
| Config Server does not register with Eureka | No Eureka client dependency on config-server | Add Eureka client to config-server | Config Server starts first — before Eureka. Adding Eureka registration would create a startup ordering issue and add unnecessary complexity. The reference has no Eureka dependency on config-server. |
| Gateway variant | Spring Cloud Gateway Server WebMVC | Spring Cloud Gateway (reactive/Netty) | The reference uses `spring-cloud-starter-gateway-server-webmvc`. All services use the Servlet stack. Mixing reactive and servlet stacks causes classloading conflicts. |

## Open Questions & Future Decisions

### Resolved

1. ✅ Config-data repo will start as a local Git repository; can be pushed to GitHub later for sharing.
2. ✅ Admin service name inconsistency will be fixed by updating the `spring.application.name` in `admin-service.yaml` to `admin-service`.

### Deferred

1. The reference `admin-service.yaml` uses `spring.application.name: admin-server`. If the instructor's grading depends on this exact name, we may need to rename the config file to `admin-server.yaml` instead. This will be verified during integration testing.

## References

- [Reference config-service](file:///Users/toporaku/code/sdwb/projecto_final/reference/config-service_20262/) — Config Server reference implementation
- [Reference registry-service](file:///Users/toporaku/code/sdwb/projecto_final/reference/registry-service_2026/) — Eureka Server reference
- [Reference gateway-service](file:///Users/toporaku/code/sdwb/projecto_final/reference/gateway-service_2026-2/) — Gateway reference
- [Reference admin-service](file:///Users/toporaku/code/sdwb/projecto_final/reference/admin-service_2026-2/) — Admin Server reference
- [Reference config-data](file:///Users/toporaku/code/sdwb/projecto_final/reference/config-data_20262/) — Config-data repository reference
- [HLD](file:///Users/toporaku/code/sdwb/projecto_final/docs/high-level-design.md) — Project-wide High-Level Design
