# SetListToPlaylist 🎵

Turn an upcoming Dublin show into a Spotify playlist based on what's most likely to be played.

Search for an artist, choose an upcoming show, and SetListToPlaylist:

1. Finds recent setlists from Setlist.fm
2. Counts how often each song has appeared
3. Predicts the most likely setlist using simple frequency
4. Finds those songs on Spotify
5. Creates a Spotify playlist

No AI is used in the product.

## Why?

I wanted to know what I'm *probably* going to hear before a show, without manually building a playlist.

There are already great tools that turn existing setlists into playlists. SetListToPlaylist takes a slightly different approach:

**What if we predict the setlist instead?**

The prediction is deliberately simple. If a song appeared in 5 out of the last 5 shows, it gets 100% confidence. If it appeared in 3 out of 5, it gets 60%.

There is no LLM, no embeddings, no agents, not even fancy statistical approaches. Just setlist data + simple maths.


## Example workflow

**Death Cab for Cutie · Dublin · 17 September 2026**

> 1. Soul Meets Body — 100%
> 2. Stone Over Water — 90%
> 3. Crooked Teeth — 90%
> 4. I Will Follow You Into the Dark — 90%
> 5. Black Sun — 80%

The predicted songs can then be turned into a Spotify playlist with the generated ULR.

## Built with
- Python
- Setlist.fm API
- Ticketmaster Discovery API
- Spotify Web API
- Spotipy

## Disclaimer

Setlists are predictions, not guarantees. Artists change their sets. That’s part of the fun.

## Running locally

Clone the repository and create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create a .env file containing your API credentials:
TICKETMASTER_API_KEY=your_key
SETLISTFM_API_KEY=your_key
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

Then run:
python3 app.py
