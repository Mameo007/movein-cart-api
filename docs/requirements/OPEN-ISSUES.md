# Open issues

Every question about the project that can't be answered yet, with who can answer it. When one is
answered, record the answer and date under **Resolved** and put the substance where it belongs: a
[business rule](business-rules.md), a [glossary](project-glossary.md) term, or a design document.
This file is a queue, not a home.

Identifiers are numbers, `OI-1` upward, added at the bottom and never reused.

**Who can answer:** "Team" means the developer can decide it alone. "Res-life" means it should be
asked of residence-life staff or an RA who has run a move-in day, if one is available. Until then
the team decides it and records the rule as a team decision.

## Priority

Ordered by the cost of a wrong guess:

1. **`OI-4`, who gets emailed.** It blocks all of #17. Residents give no email address today.
2. The rest are local to one screen or one rule. `OI-12` to `OI-16` are cleanup with an obvious
   answer, best done together in one `fix/text-consistency` pull request.

## Open

| ID | Question | Why it matters | Who can answer | Raised |
|---|---|---|---|---|
| `OI-2` | Should RAs see which carts are overdue on the public cart list, or only admins? | An admin-only endpoint (`BR-overdue-server-decides`) can't serve the public page. A "yes" adds a public endpoint or field, and the list starts showing due times it hides today. | Res-life | 2026-10-07 |
| `OI-3` | Is there a grace period before a checkout counts as overdue? | It changes one comparison in the overdue query (`BR-overdue-definition`), but also when #17 sends an overdue email. | Res-life | 2026-10-07 |
| `OI-4` | Who gets emailed, about what, and when: the resident, the admin, or both; at checkout, shortly before the due time, or once overdue? | Blocks [notifications.md](../design/notifications.md) and #17. Residents give no email address (`BR-checkout-fields`), so emailing them means a new required field on the checkout form. | Res-life | 2026-10-07 |
| `OI-5` | Should checkout reject a due time that is already past? | Today it's accepted and the checkout is overdue at once. Rejecting it is a new 400 on checkout, and the overdue tests then need another way to make a past-due checkout. | Team | 2026-10-07 |
| `OI-9` | What should happen to a due time typed into a daylight-saving gap or overlap, like 2:30 AM on the night clocks spring forward, or 1:30 AM on the night they fall back? | `to_utc()` silently picks one: the first 1:30 AM, and 3:30 AM for the 2:30 AM that doesn't exist. Nobody is told. Unlikely on move-in day, but it's undocumented. | Team | 2026-10-08 |
| `OI-10` | Should a checkout remember the timezone it was made in? | History is shown in the current site timezone. After a timezone change, a past checkout's due time displays differently from what the resident was told at the desk. | Team | 2026-10-08 |
| `OI-11` | Which timezone do emails use, and where is a time formatted on the server? | Every time is formatted in the browser today (`frontend/src/time.js`). An email from #17 is formatted by the API, which has no formatter and no timezone label yet. | Team | 2026-10-08 |
| `OI-12` | Reword the API error messages that break the writing rules in `CLAUDE.md`? `"No Active Session Found fo this Cart"` (a typo, Title Case, and "Session") in `return_cart`; `"Session not found"` and `"Session is already returned"` in `admin.py`, which should say "Checkout". Checking out a `MAINTENANCE` cart returns `"Cart is already checked out"` from `checkout_cart`, which is false for that cart; found against the running API on 2026-10-09. | It changes what the API returns. On 2026-10-08 no test asserted any `detail` text, and the frontend showed `detail` only in `AdminCarts.jsx` (cart create, status, delete), which none of these reach. Check both again before changing them. | Team | 2026-10-08 |
| `OI-13` | Fix the UI text and comments that break the writing rules? The "Sessions" heading and "No returned sessions yet." in `AdminSessions.jsx` should say "Checkouts". The placeholders "New cart number" and "Search name, room, or cart" and the "Back to carts" link aren't Title Case. A comment in `checkout_cart` misspells "raise" as "raiase". | Text only. No behavior or test changes. | Team | 2026-10-08 |
| `OI-14` | Rename `get_all_carts` or `get_sessions` so they match? One says "all" and the other doesn't, for the same kind of list endpoint. | Python names only. The URLs don't change, and the tests call the endpoints over HTTP, so nothing outside the module notices. | Team | 2026-10-08 |
| `OI-15` | Rename `admin_login` to fit the `verb_resource` pattern every other route handler uses? | Same as `OI-14`: a function name, not a URL. | Team | 2026-10-08 |
| `OI-16` | Delete the Vite starter-template leftovers? `frontend/src/App.css` (`.counter`, `.hero`, `.ticks`, and more) isn't imported anywhere; `.counter` in `index.css` is unused; `src/assets/hero.png`, `react.svg`, `vite.svg`, and `public/icons.svg` aren't referenced. `favicon.svg` and `#root` are used and stay. | Dead files that look like part of the app to anyone reading it. Check `npm run build` and the deployed site after deleting. | Team | 2026-10-08 |

## Timezone handling

What works, and why it isn't finished. `OI-9` to `OI-11` are the individual questions.

**What works.** Storage and comparison are correct and don't depend on where the server or the
browser is: every time is stored as UTC (`BR-store-utc`), "now" is `utc_now()`, and the API sends
times with a `Z`. Changing the site timezone never moves a due time. Tests cover the conversion
both ways (`test_checkout_due_at_uses_site_timezone`,
`test_admin_update_due_at_with_offset_ignores_site_timezone`).

Since 2026-10-15 the SPA reads a typed due time in the zone it showed and sends a UTC instant
(`OI-7`), and every displayed time names its zone (`OI-8`).

**What doesn't.** The app treats the timezone as a single global setting that is never recorded
with the data:

- **Data doesn't record its timezone** (`OI-10`). A checkout stores instants only, so a timezone
  change rewrites how all of history reads.
- **There is one timezone, and there should be one per organization** (`OI-6`). Designed in
  [organizations.md](../design/organizations.md), not built.
- **Edge cases are resolved silently** (`OI-9`), and **the server can't format a time** (`OI-11`).

**Suggested order.** Build organizations next, since the timezone moves onto them. `OI-9` and
`OI-10` can stay open as accepted limitations. The architecture records the single timezone as
technical debt (`TD-single-site-timezone`).

## Resolved

| ID | Question | Answer | Answered by | Date | Filed in |
|---|---|---|---|---|---|
| `OI-1` | Should the API decide what counts as overdue, or is the frontend's check enough? | The API decides, through `GET /api/admin/sessions?overdue=true`, so every device shows the same carts as overdue. | Team | 2026-10-08 | `BR-overdue-server-decides`, [overdue.md](../design/overdue.md) |
| `OI-6` | Will the app ever serve carts in more than one timezone at once? | Yes. Each organization's admin picks its organization's timezone, so the app needs one timezone per organization. Not built yet. | Team | 2026-10-15 | `BR-site-timezone`, [organizations.md](../design/organizations.md) |
| `OI-7` | Should the frontend send every typed due time as an exact instant? | Yes. The SPA reads what was typed in the zone it labelled and sends a UTC instant. The API still accepts wall-clock text. | Team | 2026-10-15 | `BR-due-times-sent-as-instants` |
| `OI-8` | Should every displayed time say which timezone it is in? | Yes. Every shown time ends with the zone's short name, like `CDT`. | Team | 2026-10-15 | `BR-times-show-zone` |
| `OI-17` | What is an organization, and how does the desk reach its cart list? | Anyone running carts, such as a college's move-in desk or a company. The owner creates each one. The desk opens the organization's link, like `/tcu`, with no login. | Team | 2026-10-15 | `BR-organization-owns-carts`, `BR-organization-created-by-owner`, `BR-organization-link`, [organizations.md](../design/organizations.md) |
| `OI-18` | How does an admin log in to their own organization, and only theirs? | With the organization's slug and its password, picked on the login page. Each password is stored hashed in the database, not in the environment. | Team | 2026-10-15 | `BR-admin-own-organization`, `BR-admin-password-hashed`, [organizations.md](../design/organizations.md) |
| `OI-19` | Which organization do the carts and checkouts already on Neon belong to? | None. They are test data, dropped during the schema change. | Team | 2026-10-15 | [organizations.md](../design/organizations.md#data-model) |
