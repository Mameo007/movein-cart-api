# Notifications design

**Area:** Email notifications, issue #17

> **Realizes:** #17
> **Depends on:** `BR-overdue-server-decides`, `BR-checkout-fields`, `BR-store-utc`, `BR-site-timezone`
> **See:** [overdue.md](overdue.md), [architecture](architectural-design.md), [open issues](../requirements/OPEN-ISSUES.md)
> **Designed against:** `e38545f`

**Status:** Blocked on `OI-4` (who gets emailed, about what, when) and `OI-11` (formatting a time
on the server). The sections below record only what's already fixed and the choices still to make.
Nothing here is a decision yet. Fill the empty sections once `OI-4` is answered, and don't build
from this document until then.

---

## Overview

The API sends email about checkouts. What triggers an email, and who receives it, depends on
`OI-4`. The overdue case reuses the overdue query from [overdue.md](overdue.md) rather than a
second definition of overdue.

## What is already fixed

These hold whatever `OI-4` decides:

- **Residents have no email address on record** (`BR-checkout-fields`). Emailing them means a new
  `email` column on `sessions` (a manual change on Neon, since there are no migrations), a new
  required field on the checkout form, and resident email addresses stored indefinitely alongside the
  other resident data (`TD-resident-data-kept-forever`). Emailing only the admin needs none of that,
  but the admin is a shared password, not a person, so the address is a setting.
- **Email is sent from the API**, the only container with the data and a secret store. The
  provider's API key is an environment variable on Render, like `ADMIN_JWT_SECRET`.
- **Times in an email are formatted on the server, in the site timezone, with the zone named**
  (for example "2:00 PM CDT"). There's no server-side formatter yet (`OI-11`).
- **The API can't wake itself up on time.** It only runs code when a request arrives, and if it's on
  Render's free plan it is spun down when idle (`RISK-render-cold-start`). Anything time-based,
  such as "email when a cart becomes overdue", needs an outside caller on a schedule.

## Choices to make once `OI-4` is answered

| Choice | Options | Depends on |
|---|---|---|
| Trigger for time-based email | (a) A scheduled GitHub Actions workflow that calls an admin-protected endpoint every few minutes. (b) A Render cron job. (c) Send only on requests that already happen, like checkout, with no time-based email at all. | Whether `OI-4` includes "nearly due" or "overdue" emails. (c) is enough if it's only a checkout confirmation. |
| Provider | A transactional email API (for example Resend, Postmark, SendGrid), or SMTP through an existing account. | Free-tier limits against the number of carts. Pick one and record the rejected ones here. |
| Sending only once | A `notified_at` column per checkout and email type, so a scheduled run doesn't email the same overdue cart every few minutes. | Any time-based trigger. Another schema change. |
| Failure handling | Log and move on, or retry on the next scheduled run. | Whether a missed email matters to res-life. |

## Components & classes

_Not designed until `OI-4` is answered._

## Sequence

_Not designed until `OI-4` is answered._

## API contract

_Not designed until `OI-4` is answered. If the trigger is a scheduled caller, this section adds its
endpoint, which belongs on the admin router so `require_admin` covers it._

## Key decisions

_None yet._

## Data model

_Depends on `OI-4`: an `email` column on `sessions` if residents are emailed, and a record of what
was sent if any email is time-based._

## Reuse & cross-cutting

- The overdue query from [overdue.md](overdue.md).
- `utc_now()` and the site timezone ([8.2.1](architectural-design.md#821-time-and-time-zones)).
- Configuration through environment variables ([8.2.5](architectural-design.md#825-configuration-and-secrets)).

## Tests

_Written with the design. Tests must never send real email: the provider client is replaced in
tests, the same way `get_db` is._

## Changes to the architecture-of-record

The email provider is already in [3](architectural-design.md#3-context-and-scope) and
[5.1](architectural-design.md#51-containers) as planned. A scheduled caller, if chosen, is added to
both.

## Open questions & risks

- `OI-4`, `OI-11`: blocking.
- `OI-3`: a grace period changes when an overdue email goes out.
- `OI-7`: if due times can still be shifted by a timezone change, an email can state the wrong
  time. Fix `OI-7` before #17.
