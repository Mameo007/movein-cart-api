# Business rules

The rules the app enforces. Terms are defined in the [glossary](project-glossary.md); questions
that are not rules yet are in [OPEN-ISSUES.md](OPEN-ISSUES.md).

Each rule has a stable `BR-<slug>` identifier. Never rename or repoint one; the sections below are
only grouping, so a rule can move between them freely.

Each rule has a **Source**: who would have to approve changing it.

- **Team decision:** chosen by the developer. Change it in a pull request.
- **Res-life policy:** set by the people running move-in. None are recorded yet. If a real
  residence-life office adopts the app, their rules go here and outrank team decisions.

**Enforced in** points at the code that is the gate. A rule that is only enforced in the frontend
is not enforced, because the public API can be called directly.

## Carts

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-cart-number-unique` | Every cart number is unique. | Team decision | `create_cart` (400) and a unique column |
| `BR-cart-one-status` | A cart is always exactly one of `AVAILABLE`, `IN_USE`, `MAINTENANCE`. | Team decision | `CartStatusUpdate`, checkout, `close_session` |
| `BR-in-use-by-checkout-only` | Only a checkout sets a cart `IN_USE`. An admin can set only `AVAILABLE` or `MAINTENANCE`. | Team decision | `CartStatusUpdate` (422) |
| `BR-in-use-cart-locked` | An `IN_USE` cart can't be edited or deleted until it's returned, so no checkout is orphaned. | Team decision | `update_cart_status`, `delete_cart` (400) |
| `BR-delete-removes-history` | Deleting a cart deletes its history too. To keep history, set it to `MAINTENANCE` instead. | Team decision | `delete_cart` |
| `BR-cart-admin-only` | Only an admin can create, edit, or delete carts. | Team decision | admin router's `require_admin` (401) |

## Checkouts

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-checkout-available-only` | Only an `AVAILABLE` cart can be checked out. | Team decision | `checkout_cart` (400) |
| `BR-checkout-fields` | A checkout records the resident's first name, last name, phone number, room number, and a due time. All are required. Format isn't checked. | Team decision | `SessionCreate` (422 if missing) |
| `BR-one-active-checkout` | A cart has at most one active checkout. | Team decision | follows from `BR-checkout-available-only` and `BR-return-in-use-only`; not safe under concurrent checkouts (`RISK-concurrent-checkout` in the [architecture](../design/architectural-design.md#11-risks-and-technical-debt)) |
| `BR-return-in-use-only` | Only an `IN_USE` cart can be returned. Returning stamps `returned_at` and frees the cart. | Team decision | `return_cart` (400), `close_session` |
| `BR-desk-no-login` | Anyone with the cart list can check out and return. The RA desk has no login. | Team decision | public router, by design |
| `BR-due-editable-while-active` | An admin can change the due time of an active checkout, earlier or later. A returned checkout's due time is fixed. | Team decision | `update_session_due_at` (400 once returned) |
| `BR-force-return` | An admin can force-return any active checkout. It has the same effect as a normal return. | Team decision | `force_return_session` via `close_session` |
| `BR-extend-from-later` | Quick-extend adds time to whichever is later, the due time or now, so extending an overdue cart always leaves it due in the future. | Team decision | `AdminSessions.jsx` (frontend only; the API accepts any due time) |
| `BR-due-per-checkout` | The due time is chosen per checkout. There is no site-wide loan length. | Team decision | `SessionCreate.due_at` |

## Overdue

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-overdue-definition` | A checkout is overdue the moment `now > due_at` and it isn't returned. No grace period. | Team decision | `isOverdue()`, frontend only, until #16 moves it to the API (`BR-overdue-server-decides`) |
| `BR-overdue-server-decides` | The API decides what counts as overdue, using the server clock, so every device shows the same carts as overdue. `GET /api/admin/sessions?overdue=true` returns only overdue checkouts. The frontend shows what the API returns and doesn't check the device clock. | Team decision (2026-10-08, `OI-1`) | Planned for #16; design in [overdue.md](../design/overdue.md) |

## Admin access and time

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-shared-admin-password` | There is one shared admin password. Logging in gives an admin token valid for 8 hours. | Team decision | `app/auth.py` |
| `BR-store-utc` | Every timestamp is stored as UTC. The site timezone only affects how times are typed in and shown, so changing it never moves a due time. | Team decision | `to_utc()`, `UTCDateTime` |
| `BR-site-timezone` | The app has one site timezone, a valid IANA name, default `America/Chicago`. A due time typed without an offset means that wall-clock time in the site timezone. | Team decision | `TimezoneUpdate` (422), `to_utc()`; the gaps are `OI-6` to `OI-11` |

## Revision history

| Date | Description |
|---|---|
| 2026-10-07 | Initial rules, written from the code at `e38545f` |
| 2026-10-08 | Added `BR-overdue-server-decides` (`OI-1`); moved open questions to `OPEN-ISSUES.md`; numeric IDs replaced with slugs |
