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
    url = f'https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={api_key}&format=json&period=7day'
    response = requests.get(url)
    data = response.json()
    tracks = data['toptracks']['track']
    return tracks
'''
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
'''
def get_song_info(title, artist):
    try:
        url = f'https://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={title}&format=json'
        response = requests.get(url)
        data = response.json()
        return data
    except:
        return None

def get_lastfm_lyrics(url):
    response = requests.get(url)
    data = response.text
    lyrics = []
    soup = BeautifulSoup(data, 'html.parser')
    span = soup.find('span', attrs={'itemprop': 'text'})
    if span is None:
        return None
    # find all p tags with class 'lyrics-paragraph'
    for p in span.find_all('p', class_='lyrics-paragraph'):
        for a in str(p).split('<br/>'):
            if a != '':
                lyrics.append(a.replace('<p class="lyrics-paragraph">', '').replace('</p>', ''))

    return {
        'lyrics': lyrics,
        'starting_point': random.randint(0, len(lyrics) - 7)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args['query']
    if query == '' or query == ' ' or query == '  ' or query is None:
        return {
            "results": []
        }
    response = requests.get(f'https://ws.audioscrobbler.com/2.0/?method=track.search&track={query}&api_key={api_key}&format=json')
    data = response.json()
    tracks = []
    for track in data['results']['trackmatches']['track']:
        tracks.append(track['name'])
    return {
        "results": tracks
    }

@app.route('/guess')
def auth():
    songs = top_tracks(request.args['username'])

    while True:
        random_song = random.choice(songs)
        data = get_lastfm_lyrics(random_song['url']+'/+lyrics')
        if data:
            random_song['lyrics'] = data
            data2 = get_song_info(random_song['name'], random_song['artist']['name'])
            if data2:
                random_song['song_data'] = data2
                break


    return render_template('app.html', song=random_song)

app.run(host='0.0.0.0', port=8080) # start app