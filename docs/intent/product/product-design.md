# Product Service Design

## Overview

The Product Service (`product-service`) manages the catalog of products, product images, and product categories for the e-commerce system. It is a core business service that provides CRUD operations for admins to manage the catalog, and query operations for other services (Cart and Invoice) to validate items and update stock during checkout.

## Architecture

This is a depth-2 leaf LLD (owning EARS directly).
It aligns with the HLD's architecture for the `PROD` segment.
- **Port:** 8083
- **Database:** `SWDB2026`
- **Eureka Name:** `PRODUCT`
- **Context Path:** `/product-service` (routed by Gateway)

## Components

### 1. Categories
- **Controller:** `CtrlCategory` handles CRUD for categories.
- **Endpoints:** GET `/category`, GET `/category/{id}`, POST `/category`, PUT `/category/{id}`, PATCH `/category/{id}/enable`, PATCH `/category/{id}/disable`.

### 2. Products
- **Controller:** `CtrlProduct` handles CRUD for products.
- **Endpoints:** GET `/product`, GET `/product/{id}`, POST `/product`, PUT `/product/{id}`, PATCH `/product/{id}/enable`, PATCH `/product/{id}/disable`.
- **New Endpoints (per HLD):**
  - `GET /product/gtin/{gtin}`: Fetches product details (including price and stock) by GTIN. Used by Cart and Invoice services to validate items. Returns 200 OK even if the product is inactive (status 0).
  - `PATCH /product/gtin/{gtin}/stock`: Decrements stock by a given positive quantity. Returns 400 Bad Request for zero or negative quantities. Returns 409 Conflict if stock is insufficient or if the product is inactive. Used by the Invoice service upon successful checkout.
  - `PATCH /product/gtin/{gtin}/stock/increment`: Increments stock by a given positive quantity. Used by the Invoice service to rollback a previously decremented stock in case of a mid-commit failure.
### 3. Product Images
- **Controller:** `CtrlProductImage` handles uploading and removing images for a product.

### 4. Security
- **JWT Authentication:** The service will use the `hasAuthority("ADMIN")` pattern from the Auth service for modifying endpoints to align roles. The new endpoints used by other services (`GET /gtin/{gtin}` and `PATCH /gtin/{gtin}/stock`) must be accessible with `hasAnyAuthority("CUSTOMER", "ADMIN")` because the Cart and Invoice services forward the client's JWT. Both `CUSTOMER` and `ADMIN` are permitted to perform these actions.
- **Actuator Security:** Explicitly permits access to `/actuator/**` without token validation to allow Spring Boot Admin Server monitoring.

## Decisions & Alternatives

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Access Control for internal APIs | Allow `CUSTOMER` and `ADMIN` authorities. | The HLD states: "The calling service forwards the client's JWT in the `Authorization` header." Both Customers and Admins can checkout. |
| GTIN Lookup Response | Return a DTO containing ID, GTIN, price, stock, and status. Returns 200 even for inactive products. | Cart and Invoice services need to check if the product exists, is active (status=1), has enough stock, and what its price is. |
| Base Reference Code | Use the instructor's reference `product-service` code and inject the Eureka client, Config client, and new GTIN endpoints. | Follows the "Reference patterns over idiomatic Spring" tenet from the HLD. |
| Negative/Zero Decrements | Return 400 Bad Request | Prevents accidental or malicious stock inflation via the decrement endpoint. |
| Mid-Commit Rollbacks | Provide `PATCH /product/gtin/{gtin}/stock/increment` | Allows the Invoice service to buffer decrements and increment them back if a subsequent item fails. |
## Data Model (from reference)
- `category` (id, category, status)
- `product` (id, gtin, product, description, price, stock, status, id_category)
- `product_image` (id_product_image, image, id_product)
