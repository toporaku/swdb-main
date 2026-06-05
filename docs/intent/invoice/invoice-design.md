# Invoice Service Design

## Overview
The `invoice-service` manages the checkout process and invoice persistence. It handles the Validate-Then-Commit checkout flow: validating cart items against product stock, applying a coupon discount, calculating taxes, saving the invoice (along with shipping and payment info), decrementing stock in `product-service`, and finally clearing the cart in `cart-service`.

## Architecture & Integration
- **Database**: `db_invoice`
- **Tables**: `invoice`, `invoice_item`
- **Dependencies**:
  - `product-service` (GET `/product/gtin/{gtin}` and PATCH `/product/gtin/{gtin}/stock`)
  - `cart-service` (GET `/cart-item/user/{userId}` and DELETE `/cart-item/user/{userId}`)
  - `auth-service` (implicitly via JWT validation)

## Data Model Additions
The reference `Invoice` entity is expanded to support the bonus features:
- `shipping_address` (VARCHAR)
- `payment_method` (VARCHAR)
- `coupon_code` (VARCHAR, nullable)

## Bonus Features
1. **Shipping**: Customer provides a shipping address during checkout, saved to the invoice.
2. **Payment**: Customer provides a payment method (e.g., "Credit Card", "PayPal") during checkout, saved to the invoice.
3. **Coupons**: Customer can optionally provide a coupon code during checkout. If provided and valid (e.g., hardcoded logic like "SAVE10" -> 10% off), a discount is applied before taxes.

## Checkout Flow (Validate-Then-Commit)
1. Receive `POST /invoice` with optional body containing `shipping_address`, `payment_method`, `coupon_code`.
2. Extract `user_id` from JWT.
3. Fetch cart items for the user from `cart-service`. If empty, return 400.
4. **Validation Phase**: Loop through cart items. Fetch product details from `product-service`. Verify `quantity <= stock`. If any item fails, return 409 (Conflict) immediately. No changes made.
5. **Commit Phase**:
   - Calculate subtotal, apply discount (if coupon valid), calculate taxes (16% of discounted subtotal), and final total.
   - Save `Invoice` and associated `InvoiceItem` records.
   - Loop through cart items and decrement stock in `product-service` (`PATCH /product/gtin/{gtin}/stock`).
   - Clear the user's cart in `cart-service` (`DELETE /cart-item/user/{userId}`).
6. Return success message.

## Security
Endpoints require authenticated users. `user_id` is extracted from the JWT.
- `POST /invoice`: Requires CUSTOMER or ADMIN role.
- `GET /invoice`: Admin gets all; Customer gets their own.
- `GET /invoice/{id}`: Admin gets any; Customer gets only if `invoice.user_id == caller.user_id`.

## Decisions & Alternatives
| Decision | Rationale | Alternatives |
|----------|-----------|--------------|
| **Coupon implementation** | Simple hardcoded evaluation for MVP (e.g. "SAVE10"). | Separate `coupon_service` or database table. Too complex for the bonus feature scope. |
| **Transactionality** | Best-effort sequential calls. Validate-then-commit avoids the most common failure (stock out) without saga complexity. | Distributed Saga. Out of scope for this project. |
| **Bonus fields on Invoice** | Add `shipping_address`, `payment_method`, `coupon_code` directly to `invoice` table. | Separate tables. Over-normalization for simple fields. |
