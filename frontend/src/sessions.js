// due_at comes back as UTC ("...Z"), so this compares exact instants and
// doesn't depend on the browser's or the site's timezone.
export function isOverdue(session, now) {
    return new Date(session.due_at) < now
}
