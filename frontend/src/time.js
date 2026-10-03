// Times from the API end in "Z" (UTC). Everything shown or typed uses the
// site's timezone from /api/settings, not whatever zone the browser is in.

export function formatTime(isoString, timeZone) {
    return new Date(isoString).toLocaleString([], { dateStyle: 'short', timeStyle: 'short', timeZone })
}

// <input type="datetime-local"> wants "YYYY-MM-DDTHH:MM" as a wall-clock time in the site's zone
export function toInputValue(date, timeZone) {
    const parts = Object.fromEntries(
        new Intl.DateTimeFormat('en-US', {
            timeZone,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hourCycle: 'h23'
        }).formatToParts(date).map(part => [part.type, part.value])
    )
    return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}

// e.g. "Central Daylight Time", for labelling where times are entered
export function timezoneLabel(timeZone) {
    return new Intl.DateTimeFormat('en-US', { timeZone, timeZoneName: 'long' })
        .formatToParts(new Date())
        .find(part => part.type === 'timeZoneName').value
}
