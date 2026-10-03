// The API sends due_at without a timezone, which the browser reads as local
// time -- the same clock the due time was typed in on.
export function isOverdue(session, now) {
    return new Date(session.due_at) < now
}
