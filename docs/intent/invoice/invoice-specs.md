# EARS: Invoice Service Specs

[x] INV-CHK-001: The system shall accept a POST request to `/invoice` to initiate checkout, extracting `user_id` from the JWT.
[x] INV-CHK-002: While checking out, the system shall fetch the user's cart from `cart-service`. If the cart is empty, the system shall return a 400 Bad Request.
[x] INV-CHK-003: During the validation phase of checkout, the system shall verify stock for all cart items against `product-service`. If any item's requested quantity exceeds available stock, the system shall return a 409 Conflict and abort checkout without saving the invoice or altering stock.
[x] INV-CHK-004: When an invoice is created, the system shall calculate item subtotal, apply any valid coupon discount, calculate taxes (16%), and calculate the final total.
[x] INV-CHK-005: When checkout is successful, the system shall persist the Invoice and its InvoiceItems.
[x] INV-CHK-006: When checkout is successful, the system shall decrement the stock of each purchased product in `product-service`.
[x] INV-CHK-007: When checkout is successful, the system shall clear the user's cart in `cart-service`.
[x] INV-CHK-008: When processing a checkout, if `shipping_address` or `payment_method` are provided in the request body, the system shall persist them on the invoice.
[x] INV-CHK-009: When processing a checkout, if a valid `coupon_code` is provided, the system shall apply a discount to the invoice subtotal.
[x] INV-SEC-001: The system shall allow an ADMIN to retrieve all invoices via GET `/invoice`.
[x] INV-SEC-002: The system shall allow a CUSTOMER to retrieve only their own invoices via GET `/invoice`.
[x] INV-SEC-003: The system shall allow a user to retrieve a specific invoice by ID via GET `/invoice/{id}` only if they are an ADMIN or the invoice belongs to them.
