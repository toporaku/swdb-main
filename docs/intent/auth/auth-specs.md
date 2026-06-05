## Registration

- [x] **AUTH-REG-001**: When an external client sends a POST request to `/user` with a valid `UserRequest` payload, the Auth Service shall hash the password using `BCryptPasswordEncoder`.
- [x] **AUTH-REG-002**: When an external client sends a POST request to `/user` with a valid `UserRequest` payload, the Auth Service shall assign the `User` role to the new account.
- [x] **AUTH-REG-003**: When an external client sends a POST request to `/user` with a valid `UserRequest` payload, the Auth Service shall persist the new user record in the `db_auth` database.
- [x] **AUTH-REG-004**: If the `UserRequest` payload is invalid (e.g., missing fields, invalid email format, weak password), the Auth Service shall reject the request with HTTP 400 Bad Request and a JSON body `{"error": "..."}`.
- [x] **AUTH-REG-005**: If the `UserRequest` contains a `username`, `email`, or `phoneNumber` that already exists, the Auth Service shall reject the request with HTTP 409 Conflict and a JSON body `{"error": "..."}`.

## Login

- [x] **AUTH-LOG-001**: When a client sends a POST request to `/login` with valid credentials, the Auth Service shall generate a JWT token signed with the secret key retrieved from Config Server.
- [x] **AUTH-LOG-002**: The generated JWT token shall include the user's `username` as the subject, and `id` and `roles` as custom claims.
- [x] **AUTH-LOG-003**: The generated JWT token shall expire 1 hour after issuance.
- [x] **AUTH-LOG-004**: When a client sends a POST request to `/login` with invalid credentials, the Auth Service shall reject the request with HTTP 401 Unauthorized and a JSON body `{"error": "..."}`.

## User Listing

- [x] **AUTH-LST-001**: When a client sends a GET request to `/user` with a valid JWT token containing the `Administrator` authority, the Auth Service shall return a list of all users mapped to `UserResponse` DTOs.
- [x] **AUTH-LST-002**: If a client sends a GET request to `/user` with a JWT token lacking the `Administrator` authority, the Auth Service shall reject the request with HTTP 403 Forbidden.
- [x] **AUTH-LST-003**: If a client sends a GET request to `/user` without a valid JWT token, the Auth Service shall reject the request with HTTP 401 Unauthorized.

## Integration

- [x] **AUTH-INT-001**: The Auth Service shall retrieve its configuration (including database credentials and JWT secret) from the Config Server.
- [x] **AUTH-INT-002**: The Auth Service shall register itself with Eureka as `auth`.
- [x] **AUTH-INT-003**: The Auth Service shall initialize a default Administrator account in the database on startup.
