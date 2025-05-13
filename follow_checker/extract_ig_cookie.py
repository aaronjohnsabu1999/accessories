import browser_cookie3
import requests

def get_ig_sessionid_from_edge():
    try:
        cookies = browser_cookie3.edge(domain_name='instagram.com')
        for cookie in cookies:
            if cookie.name == 'sessionid':
                print(f"✅ Found sessionid:\n{cookie.value}")
                return cookie.value
        print("❌ sessionid not found in Edge cookies for Instagram.")
    except Exception as e:
        print(f"❌ Failed to read cookies from Edge: {e}")

if __name__ == "__main__":
    get_ig_sessionid_from_edge()
