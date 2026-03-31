import requests
from config import URL, PAYLOAD, HEADERS, get_random_user_agent

def fetch_latest_article(verbose=False):
    """Fetch the latest news articles from Warhammer Community API."""
    try:
        headers = HEADERS.copy()
        headers["User-Agent"] = get_random_user_agent()

        res = requests.post(URL, json=PAYLOAD, headers=headers)

        if verbose:
            print("STATUS:", res.status_code)
            # Preview first 1000 characters of response
            print("RESPONSE:", res.text[:1000])

        data = res.json()
        
        # Ensure we have data
        if not data.get("news") or len(data["news"]) == 0:
            return None
            
        article = data["news"][0]

        title = article["title"]
        link = "https://www.warhammer-community.com" + article["uri"]
        date = article.get("date", "")

        return {
            "title": title,
            "link": link,
            "date": date
        }

    except Exception as e:
        print("Erreur API:", e)
        return None
