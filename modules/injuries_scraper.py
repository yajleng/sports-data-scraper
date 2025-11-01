import requests
from bs4 import BeautifulSoup

def get_injuries(team_name: str):
    """
    Scrape ESPN's updated injury report layout for CFB teams.
    Returns list of {player, status}.
    """

    try:
        # normalize team for URL (lowercase + dash)
        team_url = team_name.lower().replace(" ", "-")
        url = f"https://www.espn.com/college-football/team/injuries/_/name/{team_url}"

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # ESPN changed class names; handle new <tr> structure
        rows = soup.select("tr.Table__TR.Table__TR--sm.Table__even") or soup.select("tr.Table__TR")

        injuries = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                player = cols[0].get_text(strip=True)
                status = cols[-1].get_text(strip=True)
                if player and status:
                    injuries.append({"player": player, "status": status})

        if not injuries:
            return {"message": "no active injuries found"}

        return injuries

    except Exception as e:
        return {"error": f"injury fetch failed: {str(e)}"}
