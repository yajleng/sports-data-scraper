import requests
from bs4 import BeautifulSoup

def get_injuries(team_slug):
    """Scrape ESPN team injury page."""
    url = f"https://www.espn.com/college-football/team/injuries/_/name/{team_slug}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    injuries = []
    for row in soup.select("tr"):
        cols = [c.get_text(strip=True) for c in row.select("td")]
        if len(cols) >= 3:
            injuries.append({"player": cols[0], "status": cols[-1]})
    return injuries
