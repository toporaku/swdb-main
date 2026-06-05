# Product Segment Specs

## Categories
- `[x] PROD-CAT-001`: The system shall allow an admin to retrieve a list of all categories.
- `[x] PROD-CAT-002`: The system shall allow an admin to retrieve a specific category by its ID.
- `[x] PROD-CAT-003`: The system shall allow an admin to create a new category.
- `[x] PROD-CAT-004`: The system shall allow an admin to update an existing category.
- `[x] PROD-CAT-005`: The system shall allow an admin to logically delete (disable) a category.
- `[x] PROD-CAT-006`: The system shall allow an admin to activate an existing category.

## Products (Admin CRUD)
- `[x] PROD-MGT-001`: The system shall allow an admin to retrieve a list of all products.
- `[x] PROD-MGT-002`: The system shall allow an admin to retrieve a specific product by its ID.
- `[x] PROD-MGT-003`: The system shall allow an admin to create a new product.
- `[x] PROD-MGT-004`: The system shall allow an admin to update an existing product.
- `[x] PROD-MGT-005`: The system shall allow an admin to logically delete (disable) a product.
- `[x] PROD-MGT-006`: The system shall allow an admin to activate an existing product.
- `[x] PROD-MGT-007`: The system shall allow an admin to upload an image for a product.
- `[x] PROD-MGT-008`: The system shall allow an admin to delete an image from a product.

## Internal APIs (Used by Cart and Invoice)
- `[x] PROD-INT-001`: When a user requests a product by GTIN, the system shall return the product ID, GTIN, stock, price, and status (even if status is 0).
- `[x] PROD-INT-002`: When an invoice transaction requests a stock decrement for a GTIN with a positive quantity, the system shall reduce the stock by the requested quantity.
- `[x] PROD-INT-003`: When an invoice transaction requests a stock decrement for a GTIN and the requested quantity exceeds available stock or the product is inactive (status 0), the system shall return a 409 Conflict error and leave the stock unchanged.
- `[x] PROD-INT-004`: When a request attempts to decrement stock with a zero or negative quantity, the system shall return a 400 Bad Request error.
- `[x] PROD-INT-005`: When an invoice transaction requests a stock increment for a GTIN (e.g., for rollback), the system shall increase the stock by the requested positive quantity.

## Infrastructure & Security
- `[x] PROD-INF-001`: The product service shall register with Eureka on startup.
- `[x] PROD-INF-002`: The product service shall fetch its configuration from the Config Server on startup.
- `[x] PROD-SEC-001`: The product service shall reject requests lacking a valid JWT.
- `[x] PROD-SEC-002`: The product service shall restrict management endpoints (PROD-CAT-* and PROD-MGT-*) to users with the ADMIN role.
- `[x] PROD-SEC-003`: The product service shall allow internal endpoints (PROD-INT-*) to be called by users with the CUSTOMER or ADMIN role.
- `[x] PROD-SEC-004`: The product service shall permit access to `/actuator/**` endpoints without authentication to allow monitoring.
