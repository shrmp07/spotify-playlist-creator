from flask import Flask, request, render_template_string, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Use a secure random key 

SPOTIPY_CLIENT_ID = 'SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SCOPE = 'playlist-modify-public user-read-private'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=None,
        show_dialog=True  # Force showing auth dialog for testing
    )

HTML_TEMPLATE = """
<!doctype html>
<title>Create Spotify Playlist</title>
<h2>Paste Your YouTube-style Tracklist</h2>
<form method=post>
  <textarea name=playlist_text rows=15 cols=80 placeholder="Paste playlist here and submit...">{{playlist_text}}</textarea><br/>
  <input type=submit value='Create Spotify Playlist'>
</form>
{% if message %}
  <h3>{{ message }}</h3>
{% endif %}
{% if playlist_url %}
  <p>Your Spotify playlist was created: <a href="{{ playlist_url }}" target="_blank">{{ playlist_url }}</a></p>
{% endif %}
"""

def parse_tracklist(playlist_text):
    tracks = []
    pattern = re.compile(r'\d{2}:\d{2}\s*(?:\[.*?\])?\s*([^-\n]+)-\s*(.+)')
    lines = playlist_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            track = match.group(1).strip()
            artist = match.group(2).strip()
            tracks.append((track, artist))
        else:
            if '-' in line:
                parts = line.rsplit('-', 1)
                track, artist = parts[0].strip(), parts[1].strip()
                tracks.append((track, artist))
    return tracks

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    playlist_url = None
    playlist_text = ''

    sp_oauth = create_spotify_oauth()
    token_info = session.get('token_info', None)

    if not token_info:
        return redirect(sp_oauth.get_authorize_url())

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    sp = spotipy.Spotify(auth=token_info['access_token'])

    if request.method == 'POST':
        playlist_text = request.form['playlist_text']
        tracklist = parse_tracklist(playlist_text)

        if not tracklist:
            message = "No valid tracks found. Please check the input format."
        else:
            user_id = sp.current_user()['id']
            playlist_name = "Created from Web Input"
            playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
            playlist_id = playlist['id']

            spotify_uris = []
            for title, artist in tracklist:
                query = f'track:{title} artist:{artist}'
                result = sp.search(q=query, type='track', limit=1)
                items = result['tracks']['items']
                if items:
                    spotify_uris.append(items[0]['uri'])

            if spotify_uris:
                sp.playlist_add_items(playlist_id, spotify_uris)
                playlist_url = playlist['external_urls']['spotify']
                message = f"Playlist created with {len(spotify_uris)} tracks!"
            else:
                message = "No tracks found on Spotify matching the input."

    return render_template_string(HTML_TEMPLATE,
                                  message=message,
                                  playlist_url=playlist_url,
                                  playlist_text=playlist_text)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')

    token_info = sp_oauth.get_access_token(code)
    # Spotipy 2.x returns just token string, wrap as dict to standardize access
    if isinstance(token_info, dict):
        session['token_info'] = token_info
    else:
        session['token_info'] = {'access_token': token_info}
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
