import requests
import yaml
import time
import random
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.instagram.com/",
    "X-IG-App-ID": "936619743392459"
}

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_user_id(session, username):
    url = f"https://www.instagram.com/web/search/topsearch/?context=blended&query={username}"
    r = session.get(url)
    if r.status_code != 200:
        raise Exception(f"❌ Failed to fetch user data: {r.status_code}")
    results = r.json().get("users", [])
    for user in results:
        if user["user"]["username"].lower() == username.lower():
            return user["user"]["pk"]
    raise Exception("❌ User not found in topsearch results")

def get_follow_list(session, user_id, type="followers", max_pages=5000):
    assert type in ("followers", "following")
    url = f"https://i.instagram.com/api/v1/friendships/{user_id}/{type}/"
    results = []
    max_id = ""
    for page in range(max_pages):
        full_url = url + f"?max_id={max_id}" if max_id else url
        r = session.get(full_url)
        if r.status_code != 200:
            print(f"⚠️ Failed to fetch {type}, status {r.status_code}")
            break
        data = r.json()
        users = data.get("users", [])
        results.extend([u["username"] for u in users])
        max_id = data.get("next_max_id")
        if not max_id:
            break
        time.sleep(random.uniform(1.5, 2.5))

    # Save debug info
    with open(f"debug_{type}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results

def format_and_compare(followers, following, exclusions):
    with open("followers_formatted.txt", "w", encoding="utf-8") as f:
        f.writelines(f"{u}\n" for u in followers)
    with open("following_formatted.txt", "w", encoding="utf-8") as f:
        f.writelines(f"{u}\n" for u in following)

    with open("exclusions.txt", "r", encoding="utf-8") as f:
        excluded = set(line.strip() for line in f)

    print("\n🚨 Users you follow who don’t follow you back (excluding exclusions):\n")
    for user in following:
        if user not in followers and user not in excluded:
            print(user)

def main():
    config = load_config()
    cookies = {'sessionid': config['sessionid']}
    target = config['target_account']

    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(cookies)

    print(f"🔍 Fetching user ID for @{target}...")
    user_id = get_user_id(session, target)
    print(f"👤 User ID: {user_id}")

    print(f"📥 Getting followers...")
    followers = get_follow_list(session, user_id, "followers")
    print(f"✅ Found {len(followers)} followers")

    print(f"📤 Getting following...")
    following = get_follow_list(session, user_id, "following")
    print(f"✅ Found {len(following)} following")

    format_and_compare(followers, following, exclusions=[])
    print("✅ Done.")

if __name__ == "__main__":
    main()
