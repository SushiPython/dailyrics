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

@app.route('/get_lyrics')
def get_lyrics():
    song = request.args['song']

    genius_api = requests.get('https://genius.com/api/search/multi?per_page=1&q=' + song).json()
    #print(genius_api)
    song_name = genius_api['response']['sections'][0]['hits'][0]['result']['title']
    song_artist = genius_api['response']['sections'][0]['hits'][0]['result']['artist_names']
    url = genius_api['response']['sections'][0]['hits'][0]['result']['url']
    #print(url)
    response = requests.get(url).text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
    soup = BeautifulSoup(response, 'html.parser')
    song = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6 YYrds')

    output = song


    print(output)
    return str(output)    



@app.route('/auth')
def auth():
    print(request.args)
    auth_manager.get_access_token(request.args['code'])
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user = sp.current_user() # get user info

    songs = []

    results = sp.current_user_top_tracks(time_range='short_term', limit=50)
    for idx, item in enumerate(results['items']): # each item is a song
        song_data = {
            'id': item['id'],
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'album': item['album']['name'],
            "album_art": item['album']['images'][0]['url']
        }
        songs.append(song_data)
    random_song = random.choice(songs)
    return render_template('app.html', song=random_song)

app.run(host='0.0.0.0', port=8080) # start app