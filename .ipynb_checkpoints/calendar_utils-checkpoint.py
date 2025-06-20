import datetime
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser  # Add at top if not imported
# Config
GOOGLE_CREDS_FILE = "credentials.json"
TIMEZONE = "Asia/Kolkata"

# Timezones
IST = pytz.timezone(TIMEZONE)
UTC = pytz.utc

# Google Calendar setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=SCOPES)
calendar_service = build('calendar', 'v3', credentials=credentials)

# Helpers
def ist_to_utc(dt):
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(UTC)


def utc_to_ist(utc_str):
    """Convert UTC ISO timestamp to IST datetime object."""
    dt = datetime.datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return dt.astimezone(IST)

# Event Functions
def list_events(start_time, end_time):
    """List events between two UTC datetimes."""
    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def get_events_by_date(date_str):
    """List events for a given date string (YYYY-MM-DD) in IST."""
    date = datetime.datetime.fromisoformat(date_str)
    start = IST.localize(date.replace(hour=0, minute=0, second=0))
    end = IST.localize(date.replace(hour=23, minute=59, second=59))
    start_utc = start.astimezone(UTC)
    end_utc = end.astimezone(UTC)
    return list_events(start_utc, end_utc)

def list_events_for_month(year, month):
    """List events for the given month in IST."""
    start = IST.localize(datetime.datetime(year, month, 1))
    if month == 12:
        end = IST.localize(datetime.datetime(year + 1, 1, 1))
    else:
        end = IST.localize(datetime.datetime(year, month + 1, 1))
    return list_events(start.astimezone(UTC), end.astimezone(UTC))

def create_event(title, start_time_iso, duration_minutes):
    """Create event with start_time in IST ISO format."""
    start_ist = datetime.datetime.fromisoformat(start_time_iso)
    start_utc = ist_to_utc(start_ist)
    end_utc = start_utc + datetime.timedelta(minutes=duration_minutes)
    event = {
        'summary': title,
        'start': {'dateTime': start_utc.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_utc.isoformat(), 'timeZone': 'UTC'}
    }
    return calendar_service.events().insert(calendarId='primary', body=event).execute()

def is_conflict(start_ist, duration_minutes):
    """Check for any conflict for the given IST datetime."""
    start_utc = ist_to_utc(start_ist)
    end_utc = start_utc + datetime.timedelta(minutes=duration_minutes)
    return len(list_events(start_utc, end_utc)) > 0

def suggest_alternative(start_ist, duration_minutes, max_tries=6):
    """Suggest next available IST time slot."""
    for i in range(1, max_tries + 1):
        alt = start_ist + datetime.timedelta(minutes=i * 30)
        if not is_conflict(alt, duration_minutes):
            return alt
    return None

def delete_event_by_exact_match(title, date_str):
    """Delete event matching title on a given IST date."""
    events = get_events_by_date(date_str)
    for event in events:
        if title.lower() in event.get("summary", "").lower():
            calendar_service.events().delete(calendarId='primary', eventId=event["id"]).execute()
            return f"✅ Deleted event: {event['summary']} at {format_ist_time(event)}"
    return "⚠️ No matching event found."

def format_ist_time(event):
    """Format event start time in IST for display."""
    utc_start = event['start'].get("dateTime") or event['start'].get("date")
    ist_time = utc_to_ist(utc_start)
    return ist_time.strftime("%Y-%m-%d %H:%M")
def get_last_meeting_time():
    """Get end time of the most recent event."""
    now = datetime.datetime.now(UTC)
    past_events = list_events(now - datetime.timedelta(days=7), now)
    if not past_events:
        return None
    latest = max(past_events, key=lambda e: e['end']['dateTime'])
    return datetime.datetime.fromisoformat(latest['end']['dateTime']).astimezone(IST)

def get_usual_event_template(title_substr):
    """Return most common start time and duration for recurring events like 'sync'."""
    now = datetime.datetime.now(UTC)
    past = list_events(now - datetime.timedelta(days=60), now)
    matches = [e for e in past if title_substr.lower() in e['summary'].lower()]
    if not matches:
        return None

    # Take average duration, return last used start
    durations = []
    last_start = None
    for e in matches:
        start = datetime.datetime.fromisoformat(e['start']['dateTime'])
        end = datetime.datetime.fromisoformat(e['end']['dateTime'])
        durations.append((end - start).total_seconds() / 60)
        last_start = start.astimezone(IST)

    avg_duration = int(sum(durations) / len(durations))
    return {"start_time": last_start.isoformat(), "duration": avg_duration}
def find_next_free_slots(duration_minutes, window_days=3, granularity=30):
    """Finds next few free slots within the next `window_days`."""
    now = datetime.datetime.now(IST)
    slots = []
    for day in range(window_days):
        current = now + datetime.timedelta(days=day)
        for hour in range(8, 20):  # Working hours
            for minute in range(0, 60, granularity):
                start = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if not is_conflict(start, duration_minutes):
                    slots.append(start)
                if len(slots) >= 3:
                    return slots
    return slots
def find_free_slots_for_day(date, duration_minutes, time_pref="any"):
    slots = []
    morning_range = (7, 12)
    evening_range = (18, 22)
    full_range = (6, 22)

    hours_range = full_range
    if time_pref == "morning":
        hours_range = morning_range
    elif time_pref == "evening":
        hours_range = evening_range

    for hour in range(hours_range[0], hours_range[1]):
        dt = IST.localize(datetime.datetime(date.year, date.month, date.day, hour, 0))
        if not is_conflict(dt, duration_minutes):
            slots.append(dt)

    return slots
def get_event_time_by_title(title_substr):
    """Returns start time of the latest event containing given title."""
    now = datetime.datetime.now(UTC)
    past_events = list_events(now - datetime.timedelta(days=60), now + datetime.timedelta(days=30))
    matches = [e for e in past_events if title_substr.lower() in e['summary'].lower()]
    if not matches:
        return None
    latest = max(matches, key=lambda e: e['start']['dateTime'])
    return parser.isoparse(latest['start']['dateTime']).astimezone(IST)
