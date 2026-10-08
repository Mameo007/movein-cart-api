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

1. **`OI-6`, one timezone or several.** A "yes" changes the data model, which means a manual
   schema change on Neon, and every place a time is converted. Answer it before anything else
   touches time.
2. **`OI-7`, due times sent as wall-clock text.** A live bug, small to fix, and it widens if
   #17 starts sending emails with the wrong time in them.
3. **`OI-4`, who gets emailed.** It blocks all of #17. Residents give no email address today.
4. The rest are local to one screen or one rule. `OI-12` to `OI-16` are cleanup with an obvious
   answer, best done together in one `fix/text-consistency` pull request.

## Open

| ID | Question | Why it matters | Who can answer | Raised |
|---|---|---|---|---|
| `OI-2` | Should RAs see which carts are overdue on the public cart list, or only admins? | An admin-only endpoint (`BR-overdue-server-decides`) can't serve the public page. A "yes" adds a public endpoint or field, and the list starts showing due times it hides today. | Res-life | 2026-10-07 |
| `OI-3` | Is there a grace period before a checkout counts as overdue? | It changes one comparison in the overdue query (`BR-overdue-definition`), but also when #17 sends an overdue email. | Res-life | 2026-10-07 |
| `OI-4` | Who gets emailed, about what, and when: the resident, the admin, or both; at checkout, shortly before the due time, or once overdue? | Blocks [notifications.md](../design/notifications.md) and #17. Residents give no email address (`BR-checkout-fields`), so emailing them means a new required field on the checkout form. | Res-life | 2026-10-07 |
| `OI-5` | Should checkout reject a due time that is already past? | Today it's accepted and the checkout is overdue at once. Rejecting it is a new 400 on checkout, and the overdue tests then need another way to make a past-due checkout. | Team | 2026-10-07 |
| `OI-6` | Will the app ever serve carts in more than one timezone at once, such as two campuses or one admin managing another site? | The site timezone is one `Setting` row (`BR-site-timezone`). More than one means a timezone per location or per cart: a schema change, a new admin screen, and a different timezone lookup on every write. See [Timezone handling](#timezone-handling). | Team, then res-life | 2026-10-08 |
| `OI-7` | Should the frontend send every typed due time as an exact instant (with its UTC offset), so the API never interprets wall-clock text? | A form loaded before an admin changes the site timezone still sends wall-clock text, and the API reads it in the new zone. The due time moves by the difference between the zones, while the form's label showed the old one. | Team | 2026-10-08 |
| `OI-8` | Should every displayed time say which timezone it is in? | The admin lists show "Due 8/20/26, 2:00 PM" with no zone. Someone viewing from another timezone reads it as their own local time. Only the checkout form and settings page name the zone. | Team | 2026-10-08 |
| `OI-9` | What should happen to a due time typed into a daylight-saving gap or overlap, like 2:30 AM on the night clocks spring forward, or 1:30 AM on the night they fall back? | `to_utc()` silently picks one: the first 1:30 AM, and 3:30 AM for the 2:30 AM that doesn't exist. Nobody is told. Unlikely on move-in day, but it's undocumented. | Team | 2026-10-08 |
| `OI-10` | Should a checkout remember the timezone it was made in? | History is shown in the current site timezone. After a timezone change, a past checkout's due time displays differently from what the resident was told at the desk. | Team | 2026-10-08 |
| `OI-11` | Which timezone do emails use, and where is a time formatted on the server? | Every time is formatted in the browser today (`frontend/src/time.js`). An email from #17 is formatted by the API, which has no formatter and no timezone label yet. | Team | 2026-10-08 |
| `OI-12` | Reword the API error messages that break the writing rules in `CLAUDE.md`? `"No Active Session Found fo this Cart"` (a typo, Title Case, and "Session") in `return_cart`; `"Session not found"` and `"Session is already returned"` in `admin.py`, which should say "Checkout". | It changes what the API returns. On 2026-10-08 no test asserted any `detail` text, and the frontend showed `detail` only in `AdminCarts.jsx` (cart create, status, delete), which none of these reach. Check both again before changing them. | Team | 2026-10-08 |
| `OI-13` | Fix the UI text and comments that break the writing rules? The "Sessions" heading and "No returned sessions yet." in `AdminSessions.jsx` should say "Checkouts". The placeholders "New cart number" and "Search name, room, or cart" and the "Back to carts" link aren't Title Case. A comment in `checkout_cart` misspells "raise" as "raiase". | Text only. No behavior or test changes. | Team | 2026-10-08 |
| `OI-14` | Rename `get_all_carts` or `get_sessions` so they match? One says "all" and the other doesn't, for the same kind of list endpoint. | Python names only. The URLs don't change, and the tests call the endpoints over HTTP, so nothing outside the module notices. | Team | 2026-10-08 |
| `OI-15` | Rename `admin_login` to fit the `verb_resource` pattern every other route handler uses? | Same as `OI-14`: a function name, not a URL. | Team | 2026-10-08 |
| `OI-16` | Delete the Vite starter-template leftovers? `frontend/src/App.css` (`.counter`, `.hero`, `.ticks`, and more) isn't imported anywhere; `.counter` in `index.css` is unused; `src/assets/hero.png`, `react.svg`, `vite.svg`, and `public/icons.svg` aren't referenced. `favicon.svg` and `#root` are used and stay. | Dead files that look like part of the app to anyone reading it. Check `npm run build` and the deployed site after deleting. | Team | 2026-10-08 |

## Timezone handling

What works, and why it isn't finished. `OI-6` to `OI-11` are the individual questions.

**What works.** Storage and comparison are correct and don't depend on where the server or the
browser is: every time is stored as UTC (`BR-store-utc`), "now" is `utc_now()`, and the API sends
times with a `Z`. Changing the site timezone never moves a due time. Tests cover the conversion
both ways (`test_checkout_due_at_uses_site_timezone`,
`test_admin_update_due_at_with_offset_ignores_site_timezone`).

**What doesn't.** The app treats the timezone as a single global setting that is read again on
every request and never recorded with the data:

- **Interpretation happens late, on the server** (`OI-7`). The checkout form and the admin's due-time
  editor send `2026-08-20T14:00`, and the API decides which zone that means when the request
  arrives, not when it was typed.
- **Display has no zone label** (`OI-8`). The browser's own timezone is ignored, which is right for one
  building, but nothing tells a viewer elsewhere that the times aren't theirs.
- **Data doesn't record its timezone** (`OI-10`). A checkout stores instants only, so a timezone
  change rewrites how all of history reads.
- **There is one timezone** (`OI-6`). Supporting a second is a data-model change, not a setting.
- **Edge cases are resolved silently** (`OI-9`), and **the server can't format a time** (`OI-11`).

**Suggested order.** Answer `OI-6` first, because "yes" changes the shape of every other fix. If
the answer is "one timezone", `OI-7` and `OI-8` are small frontend changes worth doing before #17,
and `OI-9` and `OI-10` can stay open as accepted limitations. The architecture records these as
technical debt (`TD-single-site-timezone`, `TD-wall-clock-due-times`).

## Resolved

| ID | Question | Answer | Answered by | Date | Filed in |
|---|---|---|---|---|---|
| `OI-1` | Should the API decide what counts as overdue, or is the frontend's check enough? | The API decides, through `GET /api/admin/sessions?overdue=true`, so every device shows the same carts as overdue. | Team | 2026-10-08 | `BR-overdue-server-decides`, [overdue.md](../design/overdue.md) |
