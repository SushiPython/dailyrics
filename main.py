import os
import random
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

app = Flask(__name__) # init app
load_dotenv()

api_key = os.getenv('API_KEY')

def top_tracks(username):
    url = f'https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={api_key}&format=json'
    response = requests.get(url)
    data = response.json()
    tracks = data['toptracks']['track']
    return tracks


def get_lyrics(query):
    genius_api = requests.get(f'https://genius.com/api/search/multi?per_page=1&q={query}').json()
    song_name = genius_api['response']['sections'][0]['hits'][0]['result']['title']
    song_artist = genius_api['response']['sections'][0]['hits'][0]['result']['artist_names']
    image_url = genius_api['response']['sections'][0]['hits'][0]['result']['header_image_url']
    url = genius_api['response']['sections'][0]['hits'][0]['result']['url']
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    song = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6 YYrds')

    
    output = str(song).split('<br/>')
    lines = []
    for line in output:
        line_soup = BeautifulSoup(line, 'html.parser')
        line = line_soup.get_text()
        if line != '' and line.startswith('[') == False:
            lines.append(line)


    return {
        'song_name': song_name,
        'song_artist': song_artist,
        'lyrics': lines,
        'image_url': image_url,
        'starting_point': random.randint(0, len(lines) - 7)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_lyrics')
def api_get_lyrics():
    song = request.args['song']
    artist = request.args['artist']
    lyrics = get_lyrics(f'{song} {artist}')
    return lyrics


@app.route('/guess')
def auth():
    songs = top_tracks(request.args['username'])
    random_song = random.choice(songs)
    all_songs = [song['name'] for song in songs]
    random_song['lyrics'] = get_lyrics(f"{random_song['name']} {random_song['artist']['name']}")
    return render_template('app.html', song=random_song, all_songs=str(all_songs))

app.run(host='0.0.0.0', port=8080) # start app