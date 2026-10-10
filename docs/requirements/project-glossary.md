# Glossary

One name per concept. Code, docs, issues, and the UI use these terms with these meanings. When a
term in code has a different name, the **In code** column shows it.

## People

| Term | Meaning | In code |
|---|---|---|
| **Resident** | A student moving in who borrows a cart. A resident never uses the app; an RA enters their details. | `first_name`, `last_name`, `phone_number`, `room_number` on a checkout |
| **RA** (resident assistant) | Staff at the desk who check carts out and in from the public cart list. No login. | none |
| **Admin** | Anyone who knows the shared admin password. Manages carts, checkouts, and settings from `/admin`. Not tied to a person. | `require_admin`, `sub: "admin"` in the token |

## Carts and checkouts

| Term | Meaning | In code |
|---|---|---|
| **Cart** | One physical moving cart, identified to people by its cart number. | `Cart` |
| **Cart number** | The label painted or taped on the cart, e.g. `"12"`. Unique. Free text, not the database id. | `Cart.cart_number` |
| **Cart status** | Exactly one of `AVAILABLE`, `IN_USE`, `MAINTENANCE`. | `Cart.status` |
| `AVAILABLE` | On the floor and free to check out. | |
| `IN_USE` | Checked out to a resident. Only a checkout sets this. | |
| `MAINTENANCE` | Out of service. Kept in inventory with its history, but cannot be checked out. | |
| **Checkout** | One loan of one cart to one resident, from checkout to return. The core record of the app. | `Session` model, `sessions` table, `SessionResponse` |
| **Active checkout** | A checkout that hasn't been returned (`returned_at` is null). A cart has at most one. | `status=active` on `GET /api/admin/sessions` |
| **Check out** (verb) | Start a checkout: record the resident and due time, set the cart `IN_USE`. | `POST /api/carts/{id}/checkout` |
| **Return** | End a checkout: stamp `returned_at`, set the cart `AVAILABLE`. | `close_session()` |
| **Force return** | An admin ending a checkout without the RA flow, e.g. a cart found abandoned. Same effect as a return. | `POST /api/admin/sessions/{id}/return` |
| **Due time** | When the resident agreed to bring the cart back. Chosen at checkout; an admin can change it while the checkout is active. | `due_at` |
| **Overdue** | An active checkout whose due time has passed. There is no grace period. See `BR-overdue-definition` in [business rules](business-rules.md#overdue). | `?overdue=true` on `GET /api/admin/sessions` (planned, #16); today `isOverdue()` in `frontend/src/sessions.js` |
| **History** | Returned checkouts. | `status=returned` |

### Why "checkout" and not "session"

The code calls a checkout a `Session`, which collides with two other meanings in the same files:

- **SQLAlchemy `Session`**: the database session from `get_db`. The routers import the model as
  `SessionModel` to tell the two apart.
- **Login session**: an admin's signed-in period, which is really an 8-hour JWT. Call it the
  **admin token**.

In prose, issues, and UI text, say **checkout**. The `Session` class and `/sessions` URLs stay
until a rename is worth a migration on Neon.

## Time

| Term | Meaning | In code |
|---|---|---|
| **Site timezone** | The one IANA zone (default `America/Chicago`) that times are typed in and shown in. Set by an admin. See [OPEN-ISSUES.md](OPEN-ISSUES.md#timezone-handling) for its known gaps. | `Setting` row `timezone`, `get_site_timezone()` |
| **Wall-clock time** | A time typed with no offset, like `2026-08-20T14:00`. Means that time in the site timezone. | naive `datetime` input to `to_utc()` |
| **Instant** | A time with an offset, like the quick-extend buttons send. An exact point in time, whatever the site timezone. | aware `datetime` input to `to_utc()` |
| **Stored time** | Every timestamp in the database: naive UTC. Serialized with a trailing `Z`. | `utc_now()`, `UTCDateTime` |
