


# Spotify Playlist Creator - Flask App

A simple web app to create Spotify playlists from YouTube-style tracklists.

---

## How It Works

- User pastes a list of songs (one per line) in the format:  
  `00:00 Track Name - Artist Name`  
  (timestamps optional)

- The app parses the list to get track and artist names.

- It uses Spotify’s API to search for each track.

- Found tracks are added to a new playlist in the user’s Spotify account.

- The app shows a link to the created playlist.

---

## How to Use

1. Run the app locally (see installation below).

2. Open http://127.0.0.1:5000 in a browser.

3. Paste your tracklist into the provided text box.

4. Submit the form.

5. Log in and authorize the app with your Spotify account.

6. Get the link to your new Spotify playlist!

---

## Installation / Setup

- Install Python 3.7+.

- Install dependencies:  
  `pip install flask spotipy`

- Create a Spotify Developer app and get:  
  - Client ID  
  - Client Secret  
  - Set Redirect URI to `http://127.0.0.1:5000/callback`

- Add your credentials in the app’s config.

- Run `python app.py`.

---

## Input Example

```
00:00 Summertime Sadness - Lana Del Rey
03:15 Cold Brew Chapters - Tom Rosenthal
```

---

## Notes

- Only public playlists are created.

- Tracks not found on Spotify are skipped.

- Exact formatting of Redirect URI is important.

---

Feel free to try it out and create playlists easily from your favorite YouTube tracklists!
```

