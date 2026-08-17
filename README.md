# SetListToPlaylist 🎵

Predict the songs you're most likely to hear at an upcoming show, then turn that prediction into a Spotify playlist.

Search for an artist, and SetListToPlaylist:

1. Finds their 10 most recent shows on Setlist.fm
2. Shows those shows for transparency
3. Counts how often each song has appeared
4. Predicts the most likely setlist using simple frequency
5. Finds those songs on Spotify
6. Creates a Spotify playlist

No AI is used in the product.

## Why?

I wanted to know what I'm *probably* going to hear before a show, without manually building a playlist.

There are already great tools that turn existing setlists into playlists. SetListToPlaylist takes a slightly different approach:

**What if we predict the setlist instead?**

The prediction is deliberately simple.

If a song appeared in 5 out of the last 5 shows, it gets 100% confidence.

If it appeared in 3 out of 5, it gets 60%.

There is no LLM, no embeddings, no agents, and no fancy statistical model.

Just setlist data + simple maths.

## Example workflow

**Death Cab for Cutie · Dublin · 17 September 2026**

Recent Setlist.fm shows are used as evidence:

> 10 recent shows → song frequency → likely setlist

One prediction looked like:

> 1. Soul Meets Body — 100%
> 2. Stone Over Water — 90%
> 3. Crooked Teeth — 90%
> 4. I Will Follow You Into the Dark — 90%
> 5. Black Sun — 80%

The predicted songs can then be turned into a Spotify playlist.

## Built with

- Python
- Setlist.fm API
- Spotify Web API
- Spotipy

## Disclaimer

Setlists are predictions, not guarantees. Artists change their sets. That's part of the fun.

## Running locally

Clone the repository and create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt