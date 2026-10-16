// Times from the API end in "Z" (UTC). Everything shown or typed uses the
// site's timezone from /api/settings, not whatever zone the browser is in.

const DAY_MS = 24 * 60 * 60 * 1000

// e.g. "8/20/26, 2:00 PM CDT" -- the zone is named so a viewer elsewhere doesn't read it as theirs
export function formatTime(isoString, timeZone) {
    return new Date(isoString).toLocaleString([], {
        year: '2-digit',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        timeZone,
        timeZoneName: 'short'
    })
}

function wallClockParts(date, timeZone) {
    return Object.fromEntries(
        new Intl.DateTimeFormat('en-US', {
            timeZone,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hourCycle: 'h23'
        }).formatToParts(date).map(part => [part.type, part.value])
    )
}

// <input type="datetime-local"> wants "YYYY-MM-DDTHH:MM" as a wall-clock time in the site's zone
export function toInputValue(date, timeZone) {
    const parts = wallClockParts(date, timeZone)
    return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}

// How far the zone's clock is ahead of UTC at that moment, in ms (negative in the Americas)
function zoneOffsetMs(time, timeZone) {
    const p = wallClockParts(new Date(time), timeZone)
    const asUtc = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second)
    return asUtc - Math.floor(time / 1000) * 1000
}

// Turns a datetime-local value, read in the zone the form showed, into a UTC ISO string,
// so the API never has to guess which zone it was typed in. Returns null for an empty value.
// Matches to_utc() on daylight-saving edges: an ambiguous time (fall back) is the first one,
// and a time that doesn't exist (spring forward) uses the offset from before the change.
export function toInstant(inputValue, timeZone) {
    if (!inputValue) return null
    const [datePart, timePart] = inputValue.split('T')
    const [year, month, day] = datePart.split('-').map(Number)
    const [hour, minute] = timePart.split(':').map(Number)
    const asUtc = Date.UTC(year, month - 1, day, hour, minute)

    // A day either side covers any offset change near this time
    const before = asUtc - zoneOffsetMs(asUtc - DAY_MS, timeZone)
    const after = asUtc - zoneOffsetMs(asUtc + DAY_MS, timeZone)
    const isMatch = time => toInputValue(new Date(time), timeZone) === inputValue
    const instant = isMatch(before) || !isMatch(after) ? before : after
    return new Date(instant).toISOString()
}

// e.g. "Central Daylight Time", for labelling where times are entered
export function timezoneLabel(timeZone) {
    return new Intl.DateTimeFormat('en-US', { timeZone, timeZoneName: 'long' })
        .formatToParts(new Date())
        .find(part => part.type === 'timeZoneName').value
}
