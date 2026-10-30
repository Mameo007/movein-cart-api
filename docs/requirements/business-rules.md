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
| `BR-cart-number-unique` | Every cart number is unique. To be replaced by `BR-cart-number-unique-per-dorm`. | Team decision | `create_cart` (400) and a unique column |
| `BR-cart-number-unique-per-dorm` | A cart number is unique within its dorm. Two dorms can both have cart `"1"`. | Team decision (2026-10-29, `OI-17`) | Planned; design in [dorms.md](../design/dorms.md) |
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
| `BR-desk-no-login` | Anyone with the cart list can check out and return. The RA desk has no login. To be replaced by `BR-desk-code`. | Team decision | public router, by design |
| `BR-due-editable-while-active` | An admin can change the due time of an active checkout, earlier or later. A returned checkout's due time is fixed. | Team decision | `update_session_due_at` (400 once returned) |
| `BR-force-return` | An admin can force-return any active checkout. It has the same effect as a normal return. | Team decision | `force_return_session` via `close_session` |
| `BR-extend-from-later` | Quick-extend adds time to whichever is later, the due time or now, so extending an overdue cart always leaves it due in the future. | Team decision | `AdminSessions.jsx` (frontend only; the API accepts any due time) |
| `BR-due-per-checkout` | The due time is chosen per checkout. There is no site-wide loan length. | Team decision | `SessionCreate.due_at` |

## Overdue

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-overdue-definition` | A checkout is overdue the moment `now > due_at` and it isn't returned. No grace period. | Team decision | `isOverdue()`, frontend only, until #16 moves it to the API (`BR-overdue-server-decides`) |
| `BR-overdue-server-decides` | The API decides what counts as overdue, using the server clock, so every device shows the same carts as overdue. `GET /api/admin/sessions?overdue=true` returns only overdue checkouts. The frontend shows what the API returns and doesn't check the device clock. | Team decision (2026-10-08, `OI-1`) | Planned for #16; design in [overdue.md](../design/overdue.md) |

## Dorms

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-dorm-owns-carts` | Every cart belongs to one dorm, and a checkout to its cart's dorm. An admin or desk sees and changes only its own dorm's carts and checkouts; another dorm's are "not found". | Team decision (2026-10-29, `OI-17`) | Planned; design in [dorms.md](../design/dorms.md) |
| `BR-one-admin-per-dorm` | A dorm has exactly one admin, with a personal account. | Team decision (2026-10-29, `OI-18`) | Planned; a unique `admins.dorm_id` |
| `BR-admin-signup` | Creating a dorm and its admin needs an unused invite code and a school email address. Each code works once (`OI-21`). The admin can't log in until the address is verified by a link. | Team decision (2026-10-29, `OI-18`) | Planned; design in [dorms.md](../design/dorms.md) |
| `BR-admin-transfer` | The admin can hand the dorm to a new school email address. Once the new admin accepts, the old account is deleted and its token stops working. | Team decision (2026-10-29, `OI-18`) | Planned; design in [dorms.md](../design/dorms.md) |
| `BR-desk-code` | An RA device enters its dorm's desk code once. The admin can see the code and change it; changing it signs out every device that used the old one. | Team decision (2026-10-29, `OI-17`) | Planned; design in [dorms.md](../design/dorms.md) |

## Admin access and time

| ID | Rule | Source | Enforced in |
|---|---|---|---|
| `BR-shared-admin-password` | There is one shared admin password. Logging in gives an admin token valid for 8 hours. To be replaced by `BR-one-admin-per-dorm` and `BR-admin-signup`. | Team decision | `app/auth.py` |
| `BR-store-utc` | Every timestamp is stored as UTC. The site timezone only affects how times are typed in and shown, so changing it never moves a due time. | Team decision | `to_utc()`, `UTCDateTime` |
| `BR-site-timezone` | The app has one site timezone, a valid IANA name, default `America/Chicago`. A due time sent without an offset means that wall-clock time in the site timezone. Every dorm shares it, since all are on one campus (`OI-6`). Once dorms exist, only the developer changes it, not an admin. | Team decision | `TimezoneUpdate` (422), `to_utc()`; the gaps are `OI-9` to `OI-11` |
| `BR-due-times-sent-as-instants` | The SPA sends every due time as a UTC instant, reading what was typed in the timezone shown beside the input. A timezone change while a form is open can't move the due time. | Team decision (2026-10-15, `OI-7`) | `toInstant()` in `frontend/src/time.js` |
| `BR-times-show-zone` | Every time the app shows names its timezone, like "8/20/26, 2:00 PM CDT". | Team decision (2026-10-15, `OI-8`) | `formatTime()` in `frontend/src/time.js` |

## Revision history

| Date | Description |
|---|---|
| 2026-10-07 | Initial rules, written from the code at `e38545f` |
| 2026-10-08 | Added `BR-overdue-server-decides` (`OI-1`); moved open questions to `OPEN-ISSUES.md`; numeric IDs replaced with slugs |
| 2026-10-15 | Added `BR-due-times-sent-as-instants` (`OI-7`) and `BR-times-show-zone` (`OI-8`); `BR-site-timezone` notes one timezone per organization (`OI-6`) |
| 2026-10-29 | Added the planned dorm rules (`OI-17`, `OI-18`) and `BR-cart-number-unique-per-dorm`; noted which rules they replace; `BR-site-timezone` stays app-wide (`OI-6`) |
