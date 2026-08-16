import os
import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# API credentials
ticketmaster_key = os.getenv("TICKETMASTER_API_KEY")
setlist_key = os.getenv("SETLISTFM_API_KEY")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")


def search_shows(search_term):
    """Search upcoming Dublin music shows."""

    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    params = {
        "apikey": ticketmaster_key,
        "keyword": search_term,
        "city": "Dublin",
        "countryCode": "IE",
        "classificationName": "music",
        "startDateTime": "2026-08-16T00:00:00Z",
        "endDateTime": "2026-11-16T23:59:59Z",
        "size": 100,
        "sort": "date,asc",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    events = response.json().get("_embedded", {}).get("events", [])

    shows = []

    for event in events:
        attractions = event.get("_embedded", {}).get("attractions", [])

        if attractions:
            artist = attractions[0].get("name")
        else:
            artist = event["name"]

        venues = (
            event.get("_embedded", {})
            .get("venues", [])
        )

        venue = (
            venues[0].get("name", "Unknown venue")
            if venues
            else "Unknown venue"
        )

        shows.append({
            "name": event["name"],
            "artist": artist,
            "date": event["dates"]["start"].get("localDate"),
            "venue": venue,
            "id": event["id"],
        })

    return shows


def get_recent_setlists(artist):
    """Get recent setlists for an artist."""

    url = "https://api.setlist.fm/rest/1.0/search/setlists"

    headers = {
        "Accept": "application/json",
        "x-api-key": setlist_key,
    }

    params = {
        "artistName": artist,
        "p": 1,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
    )

    response.raise_for_status()

    data = response.json()

    historical_setlists = []

    for setlist in data.get("setlist", [])[:10]:
        songs = []

        for song in setlist.get("sets", {}).get("set", []):
            song_data = song.get("song", [])

            if isinstance(song_data, list):
                for item in song_data:
                    name = item.get("name")
                    if name:
                        songs.append(name)
            else:
                name = song_data.get("name")
                if name:
                    songs.append(name)

        if songs:
            historical_setlists.append({
                "date": setlist["eventDate"],
                "venue": setlist["venue"]["name"],
                "songs": songs,
            })

    return historical_setlists


def predict_setlist(historical_setlists):
    """Rank songs by how consistently they appear in recent shows."""

    song_counts = {}

    for show in historical_setlists:
        # set() means a song only counts once per show
        for song in set(show["songs"]):
            song_counts[song] = song_counts.get(song, 0) + 1

    total_shows = len(historical_setlists)

    ranked = sorted(
        song_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    likely = []

    for song, count in ranked:
        if count >= 3:
            likely.append({
                "song": song,
                "count": count,
                "confidence": round(
                    count / total_shows * 100
                ),
            })

        if len(likely) >= 15:
            break

    return likely


def create_spotify_playlist(artist, show_date, predicted_songs):
    """Create a private Spotify playlist using the current API."""

    scope = "playlist-modify-private"

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri,
            scope=scope,
            open_browser=True,
        )
    )

    playlist_name = f"Likely Setlist: {artist} · {show_date}"

    # Spotify's current endpoint is POST /me/playlists.
    playlist = sp._post(
        "me/playlists",
        payload={
            "name": playlist_name,
            "public": False,
            "description": (
                "Predicted from recent live performances. "
                "Based on song frequency across recent setlists."
            ),
        },
    )

    track_uris = []

    print("\nFinding songs on Spotify...\n")

    for item in predicted_songs:

        # Spotify's current Search API allows a maximum
        # of 10 results per request. We only need 1.
        results = sp.search(
            q=f'track:"{item["song"]}" artist:"{artist}"',
            type="track",
            limit=1,
        )

        tracks = (
            results
            .get("tracks", {})
            .get("items", [])
        )

        if tracks:
            track = tracks[0]
            track_uris.append(track["uri"])
            print(f"✓ {item['song']}")
        else:
            print(f"✗ Couldn't find: {item['song']}")

    if track_uris:
        # Spotify's current endpoint is POST /playlists/{id}/items.
        sp._post(
            f"playlists/{playlist['id']}/items",
            payload={
                "uris": track_uris,
            },
        )

    return playlist["external_urls"]["spotify"]


# -------------------------
# Main application
# -------------------------

print("\n🎵 SETLIST TO PLAYLIST\n")

search_term = input(
    "Search for an upcoming Dublin show or artist: "
).strip()

if not search_term:
    print("Please enter a search term.")
    exit()

print(f"\nSearching for '{search_term}'...\n")

shows = search_shows(search_term)

if not shows:
    print(
        f"No upcoming Dublin shows found for "
        f"'{search_term}'."
    )
    exit()

print("SHOWS FOUND:\n")

for i, show in enumerate(shows, start=1):
    print(
        f"{i}. {show['artist']} - {show['date']}\n"
        f"   {show['venue']}\n"
    )

choice = input("Choose a show number: ")

try:
    show = shows[int(choice) - 1]
except (ValueError, IndexError):
    print("Invalid choice.")
    exit()

artist = show["artist"]

print(
    f"\n{artist} · "
    f"{show['date']} · "
    f"{show['venue']}"
)

print("\nLooking up recent setlists...")

historical_setlists = get_recent_setlists(artist)

print(
    f"Found {len(historical_setlists)} "
    f"recent setlists."
)

if not historical_setlists:
    print("No historical setlists found.")
    exit()

predicted = predict_setlist(historical_setlists)

print("\nLIKELY SETLIST\n")

for i, item in enumerate(predicted, start=1):
    print(
        f"{i}. {item['song']} "
        f"({item['confidence']}% of recent shows)"
    )

confirm = input(
    "\nCreate this playlist in Spotify? [Y/n] "
)

if confirm.lower() != "n":

    print("\nConnecting to Spotify...")

    playlist_url = create_spotify_playlist(
        artist,
	show["date"],
        predicted,
    )

    print("\n🎉 Playlist created!")
    print(playlist_url)

else:
    print("\nNo playlist created.")