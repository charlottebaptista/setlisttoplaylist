import os
import requests
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()

SETLISTFM_API_KEY = os.getenv("SETLISTFM_API_KEY")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIPY_REDIRECT_URI",
    "http://127.0.0.1:8888/callback",
)


def search_setlistfm(artist_name):
    """Find an artist's recent shows on Setlist.fm."""

    headers = {
        "Accept": "application/json",
        "x-api-key": SETLISTFM_API_KEY,
    }

    response = requests.get(
        "https://api.setlist.fm/rest/1.0/search/setlists",
        headers=headers,
        params={
            "artistName": artist_name,
            "p": 1,
            "sort": "sortName",
        },
    )

    if not response.ok:
        print("\nSetlist.fm error:")
        print(response.text)
        return None

    data = response.json()
    setlists = data.get("setlist", [])

    if not setlists:
        print(
            f"\nNo recent shows found for '{artist_name}'."
        )
        return None

    return setlists[:10]


def extract_songs(setlist):
    """Extract song names from one Setlist.fm show."""

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

    return songs


def predict_setlist(setlists):
    """Predict songs based on frequency across recent shows."""

    historical_setlists = []

    for setlist in setlists:
        songs = extract_songs(setlist)

        if songs:
            historical_setlists.append(songs)

    print(
        "\nHistorical shows with usable setlists:",
        len(historical_setlists),
    )

    if not historical_setlists:
        return []

    song_counts = {}

    for songs in historical_setlists:
        for song in set(songs):
            song_counts[song] = (
                song_counts.get(song, 0) + 1
            )

    ranked_songs = sorted(
        song_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    likely_setlist = []

    for song, count in ranked_songs:

        if count >= 2:
            likely_setlist.append(
                (song, count)
            )

        if len(likely_setlist) >= 15:
            break

    print("\nLIKELY SETLIST\n")

    total_shows = len(historical_setlists)

    for number, (song, count) in enumerate(
        likely_setlist,
        start=1,
    ):
        confidence = round(
            count / total_shows * 100
        )

        print(
            f"{number}. {song} "
            f"({confidence}% of recent shows)"
        )

    print(
        f"\nPrediction based on "
        f"{total_shows} recent shows."
    )

    return likely_setlist


def create_spotify_playlist(
    artist,
    predicted_songs,
):
    """Create a Spotify playlist from the predicted songs."""

    scope = "playlist-modify-public"

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            cache_path=".spotify_cache",
            open_browser=True,
        )
    )

    playlist_name = (
        f"Likely Setlist: {artist}"
    )

    playlist = sp.current_user_playlist_create(
        name=playlist_name,
        public=True,
        description=(
            f"Predicted setlist for {artist}, "
            f"based on recent Setlist.fm shows."
        ),
    )

    track_uris = []

    for song, _ in predicted_songs:

        results = sp.search(
            q=f"artist:{artist} track:{song}",
            type="track",
            limit=1,
        )

        tracks = results.get(
            "tracks",
            {},
        ).get(
            "items",
            [],
        )

        if tracks:
            track_uris.append(
                tracks[0]["uri"]
            )

    if track_uris:
        sp.playlist_add_items(
            playlist["id"],
            track_uris,
        )

    return playlist["external_urls"]["spotify"]


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------

print("\n🎵 SETLIST TO PLAYLIST\n")

artist = input(
    "Search for an artist: "
).strip()

if not artist:
    print("Please enter an artist name.")
    raise SystemExit


print(
    f"\nSearching Setlist.fm for "
    f"'{artist}'..."
)

setlists = search_setlistfm(artist)

if not setlists:
    raise SystemExit


print("\nRECENT SHOWS\n")

for number, setlist in enumerate(
    setlists,
    start=1,
):

    event_date = setlist.get(
        "eventDate",
        "Unknown date",
    )

    venue = setlist.get(
        "venue",
        {},
    )

    venue_name = venue.get(
        "name",
        "Unknown venue",
    )

    city = venue.get(
        "city",
        {},
    )

    city_name = city.get(
        "name",
        "",
    )

    location = venue_name

    if city_name:
        location += f", {city_name}"

    print(
        f"{number}. "
        f"{event_date} · "
        f"{location}"
    )


predicted = predict_setlist(
    setlists
)

if not predicted:
    print(
        "\nCouldn't generate "
        "a likely setlist."
    )

    raise SystemExit


create_playlist = input(
    "\nCreate this playlist in Spotify? [Y/n] "
).strip().lower()


if create_playlist in (
    "",
    "y",
    "yes",
):

    playlist_url = create_spotify_playlist(
        artist,
        predicted,
    )

    print("\n✓ Playlist created!")
    print(playlist_url)

else:

    print(
        "\nNo playlist created."
    )