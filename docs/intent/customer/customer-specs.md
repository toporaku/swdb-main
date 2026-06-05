# Customer Service Specs (EARS)

[x] CUST-REG-001: **When** a GET request is sent to `/region`, **then** the system returns a list of all registered regions.
[x] CUST-REG-002: **When** a GET request is sent to `/region/active`, **then** the system returns a list of only active regions (status = 1).
[x] CUST-REG-003: **When** a POST request is sent to `/region` by an ADMIN, **then** the system validates the request body and persists the new Region in the database with status = 1.
[x] CUST-REG-004: **When** a PUT request is sent to `/region/{id}` by an ADMIN, **then** the system validates the request body and updates the region record.
[x] CUST-REG-005: **When** a PATCH request is sent to `/region/{id}/enable` by an ADMIN, **then** the system sets the region status to 1.
[x] CUST-REG-006: **When** a PATCH request is sent to `/region/{id}/disable` by an ADMIN, **then** the system sets the region status to 0.

[x] CUST-PROFILE-001: **When** a GET request is sent to `/customer` by an ADMIN, **then** the system returns a list of all customer profiles.
[x] CUST-PROFILE-002: **When** a GET request is sent to `/customer/{id}` by an authorized user, **then** the system returns the detailed customer profile matching the ID.
[x] CUST-PROFILE-003: **When** a POST request is sent to `/customer` by an authorized user, **then** the system validates the input, checks that the region exists and is active, and registers the customer profile.
[x] CUST-PROFILE-004: **When** a PUT request is sent to `/customer/{id}` by an authorized user, **then** the system validates the input, checks that the customer and region exist, and updates the customer profile.
[x] CUST-PROFILE-005: **When** a PATCH request is sent to `/customer/{id}/enable` by an ADMIN, **then** the system sets the customer status to 1.
[x] CUST-PROFILE-006: **When** a PATCH request is sent to `/customer/{id}/disable` by an ADMIN, **then** the system sets the customer status to 0.

[x] CUST-IMAGE-001: **When** a POST request is sent to `/customer-image` by an authorized user, **then** the system validates the input, saves the base64-encoded image to the local filesystem directory, and persists the metadata record in the database.
