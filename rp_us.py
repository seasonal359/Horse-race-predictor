# rp_us.py - U.S. Racing Post Scraper Module (All U.S. Thoroughbred Tracks)

import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.racingpost.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Mapping of U.S. Thoroughbred track names to their Racing Post location codes
TRACK_CODES = {
    "Churchill Downs": 308,
    "Gulfstream Park": 272,
    "Santa Anita": 257,
    "Belmont Park": 259,
    "Aqueduct": 270,
    "Keeneland": 304,
    "Oaklawn Park": 258,
    "Fair Grounds": 300,
    "Tampa Bay Downs": 285,
    "Del Mar": 277,
    "Saratoga": 273,
    "Laurel Park": 305,
    "Louisiana Downs": 299,
    "Mountaineer": 307
}

def get_race_links(track_name, date_str):
    """
    Scrape races for a given U.S. track and date (YYYY-MM-DD).
    Returns a list of (race_name, race_time, race_url).
    """
    track_id = TRACK_CODES.get(track_name)
    if not track_id:
        return []

    date_url = f"{BASE_URL}/racecards/{track_id}/{track_name.lower().replace(' ', '-')}/{date_str}"
    response = requests.get(date_url, headers=HEADERS)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    races = []

    race_containers = soup.select("div.rc-meeting-info__race")
    for race in race_containers:
        time_elem = race.select_one(".rc-meeting-info__time")
        link_elem = race.select_one("a.rc-meeting-info__link")
        if time_elem and link_elem:
            time_str = time_elem.text.strip()
            href = link_elem.get("href")
            race_name = link_elem.text.strip()
            races.append((race_name, time_str, BASE_URL + href))

    return races

def get_race_horses(race_url):
    """
    Scrape a given race's page and return horse info.
    """
    response = requests.get(race_url, headers=HEADERS)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    horses = []
    rows = soup.select(".racecard-number__row")

    for row in rows:
        try:
            name_elem = row.select_one(".racecard-horse-name")
            odds_elem = row.select_one(".racecard-price")
            jockey_elem = row.select_one(".racecard-jockey")
            trainer_elem = row.select_one(".racecard-trainer")

            horses.append({
                "name": name_elem.text.strip() if name_elem else "Unknown",
                "odds": odds_elem.text.strip() if odds_elem else "N/A",
                "jockey": jockey_elem.text.strip() if jockey_elem else "",
                "trainer": trainer_elem.text.strip() if trainer_elem else "",
            })
        except Exception:
            continue

    return horses

if __name__ == "__main__":
    # Test all tracks today
    today_str = datetime.today().strftime("%Y-%m-%d")
    for track in TRACK_CODES:
        print(f"\n--- {track} ({today_str}) ---")
        races = get_race_links(track, today_str)
        print(f"Found {len(races)} races.")
        for name, time_str, url in races:
            print(f"{time_str} - {name} -> {url}")
            horses = get_race_horses(url)
            for h in horses:
                print("  ", h)
