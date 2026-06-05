# Cart Service Specifications (EARS)

## External API
- `[x]` CART-EXT-001: The system shall allow a customer to add an item to their cart via `POST /cart-item` if the requested quantity is available in stock.
- `[x]` CART-EXT-002: The system shall return a 400 Bad Request if the customer attempts to add an item with a quantity exceeding available stock.
- `[x]` CART-EXT-003: The system shall allow a customer to view their cart items via `GET /cart-item/user/{userId}`.
- `[x]` CART-EXT-004: The system shall allow a customer to remove an item from their cart via `DELETE /cart-item/{id}`.
- `[x]` CART-EXT-005: The system shall allow a customer to clear their cart via `DELETE /cart-item/user/{userId}`.

## Internal API (Used by Invoice Service)
- `[x]` CART-INT-001: The system shall allow internal services to retrieve all cart items for a user via `GET /cart-item/user/{userId}`.
- `[x]` CART-INT-002: The system shall allow internal services to clear a user's cart via `DELETE /cart-item/user/{userId}`.

## Security
- `[x]` CART-SEC-001: The system shall deny access to cart operations without a valid JWT token.
- `[x]` CART-SEC-002: The system shall allow a customer to access only their own cart items (matching `user_id` from JWT claim).
- `[x]` CART-SEC-003: The system shall allow an administrator to access any user's cart items.
