import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import dotenv
import string
import random
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__) # init app
dotenv.load_dotenv() # make sure you have an env file

def get_lyrics(query):
    genius_api = requests.get(f'https://genius.com/api/search/multi?per_page=1&q={query}').json()
    #print(genius_api)
    song_name = genius_api['response']['sections'][0]['hits'][0]['result']['title']
    song_artist = genius_api['response']['sections'][0]['hits'][0]['result']['artist_names']
    url = genius_api['response']['sections'][0]['hits'][0]['result']['url']
    #print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    song = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6 YYrds')

    
    output = str(song).split('<br/>')
    lines = []
    for line in output:
        line_soup = BeautifulSoup(line, 'html.parser')
        line = line_soup.get_text()
        print(f'.{line}.')
        if line != '' and line.startswith('[') == False:
            lines.append(line)


    return {
        'song_name': song_name,
        'song_artist': song_artist,
        'lyrics': lines
    }

def gen_rand_str(len):
    return ''.join(random.choice(string.ascii_letters) for _ in range(len))

auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'), #env file
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'), #env file
    redirect_uri="http://localhost:8080/auth", #change this to whatever port
    scope="user-top-read", #reading top songs
    cache_path=f"cache/.cache-spotipy-{gen_rand_str(10)}" # spotipy forces me to cache this
)
url = auth_manager.get_authorize_url()

@app.route('/')
def index():
    return render_template('index.html', url=url)

@app.route('/api/get_lyrics')
def api_get_lyrics():
    song = request.args['song']
    artist = request.args['artist']
    lyrics = get_lyrics(f'{song} {artist}')
    return lyrics



@app.route('/auth')
def auth():
    print(request.args)
    auth_manager.get_access_token(request.args['code'])
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user = sp.current_user() # get user info

    songs = []

    results = sp.current_user_top_tracks(time_range='long_term', limit=500)
    all_songs = []
    for idx, item in enumerate(results['items']): # each item is a song
        song_data = {
            'id': item['id'],
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'album': item['album']['name'],
            "album_art": item['album']['images'][0]['url'],
            "name_lower": item['name'].lower(),
        }
        songs.append(song_data)
        all_songs.append(item['name'])
    random_song = random.choice(songs)
    random_song['lyrics'] = get_lyrics(f"{random_song['name']} {random_song['artist']}")
    print(len(all_songs))
    return render_template('app.html', song=random_song, all_songs=str(all_songs))

app.run(host='0.0.0.0', port=8080) # start app