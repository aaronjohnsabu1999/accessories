import datetime
import os
import re
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ics import Calendar, Event

# Constants
READ_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
WRITE_SCOPES = ['https://www.googleapis.com/auth/calendar']
KEYWORDS_FILE = 'keywords.txt'
DELETE_IDS_FILE = 'delete_ids.txt'
OUTPUT_ICS = 'filtered_entries.ics'

def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        print(f"❌ No '{KEYWORDS_FILE}' found. Create one with keywords per line.")
        sys.exit(1)
    with open(KEYWORDS_FILE, 'r') as f:
        return [line.strip().lower() for line in f if line.strip()]

def keyword_match(summary, keywords):
    return any(re.search(rf'\b{k}\b', summary, re.IGNORECASE) for k in keywords)

def authenticate(scopes):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def display_event(event):
    start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', '[No Title]')
    location = event.get('location', '')
    description = event.get('description', '')
    print(f"\n---\n📅 {start} | {summary}")
    if location:
        print(f"📍 Location: {location}")
    if description:
        print(f"📝 Description: {description}")

def entry_chooser():
    service = authenticate(READ_SCOPES)
    keywords = load_keywords()
    events_result = service.events().list(
        calendarId='primary',
        timeMin='2023-11-01T00:00:00Z',
        maxResults=5000,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    print(f"🔍 Found {len(events)} events total.")

    selected_ids = []

    for event in events:
        summary = event.get('summary', '')
        if keyword_match(summary, keywords):
            display_event(event)
            choice = input("Add this to delete list? (y/n): ").strip().lower()
            if 'y' in choice:
                selected_ids.append(event['id'])

    with open(DELETE_IDS_FILE, 'w') as f:
        f.writelines([f"{eid}\n" for eid in selected_ids])

    print(f"\n✅ Saved {len(selected_ids)} event IDs to '{DELETE_IDS_FILE}'.")

def export_ics_from_ids():
    service = authenticate(READ_SCOPES)

    if not os.path.exists(DELETE_IDS_FILE):
        print(f"❌ '{DELETE_IDS_FILE}' not found.")
        return

    with open(DELETE_IDS_FILE, 'r') as f:
        ids_to_export = [line.strip() for line in f if line.strip()]

    calendar = Calendar()
    count = 0

    for eid in ids_to_export:
        try:
            event = service.events().get(calendarId='primary', eventId=eid).execute()
            e = Event()
            e.name = event.get('summary', '[No Title]')
            e.begin = event['start'].get('dateTime', event['start'].get('date'))
            e.end = event['end'].get('dateTime', event['end'].get('date'))
            e.description = event.get('description', '')
            e.location = event.get('location', '')
            calendar.events.add(e)
            print(f"📦 Exported: {e.name}")
            count += 1
        except Exception as e:
            print(f"⚠️ Failed to fetch event ID {eid}: {e}")

    with open(OUTPUT_ICS, 'w') as f:
        f.writelines(calendar.serialize_iter())

    print(f"\n✅ Finished exporting {count} events to '{OUTPUT_ICS}'")

def safe_delete():
    service = authenticate(WRITE_SCOPES)

    if not os.path.exists(DELETE_IDS_FILE):
        print("❌ 'delete_ids.txt' not found.")
        return

    with open(DELETE_IDS_FILE, 'r') as f:
        ids_to_delete = [line.strip() for line in f if line.strip()]

    confirmed_ids = []
    for eid in ids_to_delete:
        try:
            service.events().get(calendarId='primary', eventId=eid).execute()
            confirmed_ids.append(eid)
        except Exception as e:
            print(f"⚠️ Event ID not found (skipped): {eid} — {e}")

    if len(confirmed_ids) < len(ids_to_delete):
        print("\n⚠️ Warning: Some events are missing. Aborting deletion.")
        return

    print(f"\n⚠️ All {len(confirmed_ids)} events found. Ready to delete from your calendar.")
    confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled.")
        return

    for eid in confirmed_ids:
        try:
            service.events().delete(calendarId='primary', eventId=eid).execute()
            print(f"🗑️ Deleted event ID: {eid}")
        except Exception as e:
            print(f"⚠️ Failed to delete event ID {eid}: {e}")

    print("✅ Deletion complete.")

def main():
    while True:
        print("Select mode:")
        print("1. Entry Chooser (select + save IDs)")
        print("2. Export to ICS (based on saved IDs)")
        print("3. Safe Deleter (only deletes if valid IDs)")
        mode = input("Enter 1, 2, or 3: ").strip()

        if mode == '1':
            entry_chooser()
            break
        elif mode == '2':
            export_ics_from_ids()
            break
        elif mode == '3':
            safe_delete()
            break
        else:
            print("❌ Invalid choice. Choose again.\n\n")

if __name__ == '__main__':
    main()
