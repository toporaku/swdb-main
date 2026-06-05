# Cart Service Design

## Overview
The `cart-service` is responsible for managing customer shopping carts. It provides CRUD operations on cart items and exposes internal endpoints for the checkout process (managed by the `invoice-service`). 
It connects to its own database (`db_cart`) and uses `product-service` to validate product existence, price, and stock levels before adding items to the cart.

## Database Schema
**Database**: `db_cart`
**Table**: `cart_item`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, Auto Increment |
| cart_id | INT | Not Null (Used as `user_id`) |
| gtin | VARCHAR(15) | Not Null |
| quantity | INT | Not Null, > 0 |

## Dependencies
- **Eureka Server**: For service discovery.
- **Config Server**: For externalized configuration (`cart.properties`).
- **Product Service**: Called via `RestTemplate` (e.g. `http://PRODUCT/product/gtin/{gtin}`) to get product details (price, stock).

## Endpoints

### External
- `POST /cart-item`: Adds an item to the cart. Validates with `product-service` that requested quantity <= stock.
- `GET /cart-item/user/{user_id}`: Retrieves all cart items for a given user. (Wait, `cart_id` in the DB schema is usually the `user_id` as they are 1:1, or we just map it. The reference code usually ties `user_id` -> `cart_id`). Actually, let's just use `cart_id` as `user_id` directly for simplicity, or keep `cart_id`. The HLD says `GET /cart-item/user/{userId}`.
- `DELETE /cart-item/{id}`: Removes a specific item from the cart.
- `DELETE /cart-item/user/{userId}`: Clears the cart (also used internally by `invoice-service`).

### Security
Uses the `JwtAuthFilter` pattern with `user_id` extraction. Users can only access their own cart items. Admins can access anyone's.

## Decisions & Alternatives
| Decision | Rationale | Alternatives |
|----------|-----------|--------------|
| **Cart representation** | Items stored directly linked to a user. No separate "Cart" entity. | Creating a `cart` table. Unnecessary complexity since carts don't hold metadata other than `user_id`. |
| **Validation Strategy** | Check stock immediately upon adding to cart. | Defer all checks to checkout. We do both: fail early on add, and fail safe on checkout. |
