# Low-Level Design: Auth Service

## Goal

The Auth Service manages user identities and issues JWT tokens. It serves as the primary entry point for user registration and authentication within the e-commerce microservices ecosystem. It relies on its own independent database (`db_auth`) for user records.

## Component Boundaries

- **Upstream:** API Gateway routes `/auth-service/**` traffic here.
- **Downstream:** A dedicated local MySQL database.
- **Lateral:** Config Server provides application properties; Eureka provides service discovery. No direct lateral communication with other business services (other services validate the JWT token locally without calling Auth Service).

## Database Schema Mapping

- **Database name:** `db_auth`
- **Entities:**
  - `User`: Stored in table `user`. Columns: `id`, `username` (unique), `email` (unique), `password`, `name`, `lastName`, `phoneNumber` (unique).
  - `user_roles`: Element collection table joining `user_id` to a `roles` string column.

## Core Logic

### 1. User Registration (`POST /user`)
- Accepts a JSON payload containing `username`, `email`, `password`, `name`, `lastName`, and `phoneNumber`.
- Validates the payload using `jakarta.validation` annotations (e.g., password regex requiring 8+ chars, uppercase, number, and special char).
- Hashes the password using `BCryptPasswordEncoder`.
- Hardcodes the `User` role (`user.setRoles(Set.of("User"))`).
- Persists to the database.

### 2. User Authentication (`POST /login`)
- Accepts a JSON payload with `username` and `password`.
- Uses Spring Security's `AuthenticationManager` to authenticate the credentials against the database records.
- Generates a JWT token valid for 1 hour using a secret key (loaded from Config Server). The token payload includes the `username` (subject), `id`, and `roles`.
- Returns the token in a JSON response `{"token": "..."}`.

### 3. User Listing (`GET /user`)
- Retrieves a list of all registered users.
- Maps the internal `User` entity to a `UserResponse` DTO to avoid exposing the hashed password.
- Secured endpoint: Requires a valid JWT token with the `Administrator` authority.

## Decisions & Alternatives

| Decision | Chosen Option | Rejected Alternatives | Rationale |
|----------|---------------|-----------------------|-----------|
| **JWT Secret Location** | Externalize to Config Server | Hardcode in source code | Hardcoding secrets violates basic security practices and twelve-factor app principles. |
| **Admin User Creation** | Database seeder / Manual SQL | Dedicated endpoint, Pass role in registration | The reference implementation hardcodes the "User" role for all new registrations. Rather than deviating from the reference by modifying the registration endpoint, we will initialize an Admin user directly in the database. |
| **Database Name** | `db_auth` | `dwb2026_2` | The reference uses an arbitrary database name. Standardizing on `db_auth` is clearer and aligns with `db_cart` and `db_invoice`. |
