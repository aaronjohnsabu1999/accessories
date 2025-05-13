# 🧰 Accessories

A curated toolbox of personal scripts for automating life tasks. Right now it includes:

## 📆 `calendar_modifier/`

**Google Calendar event selector + safe deleter.**

### Features:
- Scan your calendar for events containing keywords like "boba", "dinner", etc.
- Manually select which events to mark for export
- Export selected events to `.ics`
- Safely delete them *only after verification* (optional)

### Setup:
1. Create `keywords.txt` (one keyword per line)
2. Add your `credentials.json` from Google Cloud Console
3. Run `main.py`

## 🔍 `follow_checker/`

**Instagram follower/following mismatch detector.**

### Features:
- Uses your IG session cookie to access follower/following data (non-public API)
- Prints who you follow that doesn’t follow you back
- Optionally excludes friends via `exclusions.txt`

### Setup:
1. Create a `config.yaml`:

```yaml
sessionid: "YOUR_SESSION_ID"
target_account: officialaaronjs
```

2. Create `exclusions.txt` (one username per line to ignore)
3. Run `main.py`

## 📦 Installation

Each folder has its own dependencies:

```bash
cd calendar_modifier
pip install -r requirements.txt

cd ../follow_checker
pip install -r requirements.txt
```

## 🧪 License

MIT — use it, fork it, remix it. Don’t sell access to it like a toolbag.