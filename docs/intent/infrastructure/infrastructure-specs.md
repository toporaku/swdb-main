## Config Server

- [x] **INFRA-CFG-001**: The Config Server shall start on port 8888 and serve configuration to all client services.
- [x] **INFRA-CFG-002**: The Config Server shall read configuration files from a Git repository specified by `spring.cloud.config.server.git.uri`.
- [x] **INFRA-CFG-003**: When a client service requests configuration, the Config Server shall match the request to a file named `{spring.application.name}.{yaml|properties}` in the Git repository and return its contents.
- [x] **INFRA-CFG-004**: The Config Server shall use `master` as the default Git branch label.
- [x] **INFRA-CFG-005**: The Config Server shall not register with Eureka (no Eureka client dependency).

## Config-Data Repository

- [x] **INFRA-DATA-001**: The config-data repository shall contain a configuration file for every service that uses Config Server, named to match that service's `spring.application.name`.
- [x] **INFRA-DATA-002**: The config-data repository shall contain gateway route definitions for all five business services (auth, product, cart, invoice, customer) under `spring.cloud.gateway.server.webmvc.routes`, each with a `StripPrefix=1` filter.
- [x] **INFRA-DATA-003**: Each business service's config-data file shall include Eureka client registration properties (`eureka.client.service-url.defaultZone`, `eureka.client.register-with-eureka=true`, `eureka.client.fetch-registry=true`).
- [x] **INFRA-DATA-004**: Each business service's config-data file shall expose Actuator endpoints (`health,info,metrics,loggers,threaddump,heapdump`) with `management.endpoint.health.show-details=always` for Spring Boot Admin monitoring.
- [ ] **INFRA-DATA-005**: The gateway-service config-data file shall expose Actuator endpoints (`health,info,metrics,loggers,threaddump,heapdump`) with `management.endpoint.health.show-details=always` for Spring Boot Admin monitoring.

## Registry Service (Eureka)

- [x] **INFRA-REG-001**: The Registry Service shall run as a Eureka Server on port 8761.
- [x] **INFRA-REG-002**: The Registry Service shall pull its configuration from Config Server via `spring.config.import=optional:configserver:` pointing at `http://localhost:8888`.
- [x] **INFRA-REG-003**: The Registry Service shall not register with itself (`eureka.client.register-with-eureka=false`, `eureka.client.fetch-registry=false`).
- [x] **INFRA-REG-004**: The Registry Service shall provide a web dashboard at `http://localhost:8761` listing all registered service instances.

## Gateway Service

- [x] **INFRA-GW-001**: The Gateway Service shall run as a Spring Cloud Gateway (WebMVC variant) on port 8080.
- [x] **INFRA-GW-002**: The Gateway Service shall pull its configuration from Config Server and register with Eureka.
- [x] **INFRA-GW-003**: When an external client sends a request matching `/auth-service/**`, the Gateway shall forward it to `lb://AUTH` with the first path segment stripped.
- [x] **INFRA-GW-004**: When an external client sends a request matching `/product-service/**`, the Gateway shall forward it to `lb://PRODUCT` with the first path segment stripped.
- [x] **INFRA-GW-005**: When an external client sends a request matching `/cart-service/**`, the Gateway shall forward it to `lb://CART-SERVICE` with the first path segment stripped.
- [x] **INFRA-GW-006**: When an external client sends a request matching `/invoice-service/**`, the Gateway shall forward it to `lb://INVOICE` with the first path segment stripped.
- [x] **INFRA-GW-007**: When an external client sends a request matching `/customer-service/**`, the Gateway shall forward it to `lb://CUSTOMER-SERVICE` with the first path segment stripped.
- [x] **INFRA-GW-008**: If an external client sends a request that does not match any configured route, then the Gateway shall return HTTP 404.
- [x] **INFRA-GW-009**: If a route's target service is not registered in Eureka, then the Gateway shall return HTTP 503.

## Admin Service

- [x] **INFRA-ADM-001**: The Admin Service shall run as a Spring Boot Admin Server on port 9090.
- [x] **INFRA-ADM-002**: The Admin Service shall pull its configuration from Config Server and register with Eureka.
- [x] **INFRA-ADM-003**: The Admin Service shall discover monitored services via Eureka (`spring.boot.admin.discovery.enabled=true`) and display their health status on a web dashboard.

## Business Service Integration

- [ ] **INFRA-INT-001**: Every business service (auth, product, cart, invoice, customer) shall include `spring-cloud-starter-config` and `spring-cloud-starter-netflix-eureka-client` as Maven dependencies.
- [ ] **INFRA-INT-002**: Every business service shall connect to Config Server on startup via `spring.config.import=optional:configserver:` pointing at `http://localhost:8888`.
- [ ] **INFRA-INT-003**: Every business service shall register with Eureka using its `spring.application.name` as the service identifier.
- [ ] **INFRA-INT-004**: Every business service shall use Spring Boot 4.0.6, Spring Cloud 2025.1.1, and Java 21.
