---
node: infrastructure
---

# Decision: Admin Service Application Naming

## Context

The instructor's reference implementation for the admin service contains a naming inconsistency: the Maven project, source directory, and config-data file are named `admin-service`, but the `application.yaml` file inside the config-data repository sets `spring.application.name: admin-server`.

Spring Cloud Config Server maps a requesting client to a configuration file by matching the requesting client's `spring.application.name` to the configuration file's base name (e.g., a client named `admin-service` gets `admin-service.yaml`).

If a client requests config as `admin-service`, it receives `admin-service.yaml`, which then overrides its internal name to `admin-server`. It subsequently registers with Eureka as `admin-server`. We must resolve this discrepancy before implementing the service.

## Decision Elements

- **Configuration Integrity (Gate):** The configuration file name in `config-data/` must match the `spring.application.name` the service uses to bootstrap and connect to the Config Server.
- **Consistency with artifact ID (Moderate):** The application name should ideally match the Maven `artifactId` and directory name (`admin-service`).
- **Safety from grading penalization (Major):** The course instructor will grade the project. Adhering to the instructor's reference patterns reduces the risk of automated or manual grading scripts failing. Tenet: *Course-aligned over production-grade*.

## Options in the Domain

### Option A: Standardize on `admin-service`

Standardize the name across all artifacts. Update the `spring.application.name` inside `admin-service.yaml` to be `admin-service`, matching the config file name, POM artifact ID, and directory.

- **Configuration Integrity:** passes. (Service bootstraps as `admin-service`, gets `admin-service.yaml`, name remains `admin-service`).
- **Consistency with artifact ID:** strong fit.
- **Safety from grading penalization:** partial fit. Modifies the reference's internal property value, which might be a problem if grading checks for the exact Eureka registration name `admin-server`.

### Option B: Standardize on `admin-server`

Standardize around the internal property name. Rename the config file to `admin-server.yaml`, rename the Maven artifact ID to `admin-server`, and have the service bootstrap as `admin-server`.

- **Configuration Integrity:** passes. (Service bootstraps as `admin-server`, gets `admin-server.yaml`, name remains `admin-server`).
- **Consistency with artifact ID:** strong fit. (Requires renaming POM and directory to match).
- **Safety from grading penalization:** partial fit. Modifies the reference's directory and POM names.

### Option C: Keep the Inconsistency (Bootstrap as `admin-service`, run as `admin-server`)

Leave the configuration file named `admin-service.yaml` and the POM/directory as `admin-service`. Let the bootstrap properties define `name: admin-service` so Config Server matches the file, but keep `name: admin-server` inside `admin-service.yaml` so the service registers with Eureka as `admin-server`.

- **Configuration Integrity:** passes. (Technically works, although relies on overriding the property mid-startup).
- **Consistency with artifact ID:** weak fit. (The service registers under a different name than its artifact).
- **Safety from grading penalization:** strong fit. Leaves the reference code exactly as provided by the instructor.

## Selection

We select **Option A (Standardize on `admin-service`)**. 

Despite the *Course-aligned over production-grade* tenet typically favoring Option C (leaving the reference exactly as is), Option A is selected because the discrepancy is almost certainly an oversight in the reference material rather than an intentional design. Standardizing on `admin-service` ensures alignment across the file system (directory name), build system (POM artifact), Config Server matching (file name), and service discovery (Eureka registration). 

If during integration testing it is discovered that another service hardcodes a URL to `http://admin-server` or a grading rubric strictly requires the Eureka ID to be `ADMIN-SERVER`, we will revisit this and pivot to Option C.
