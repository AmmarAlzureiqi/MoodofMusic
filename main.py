import requests
import urllib.parse
import os
import spotipy
import base64
import openai
import mysql.connector

from flask import Flask, redirect, request, jsonify, session, render_template, url_for, flash, g
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils import create_playlist_fun, generate_image, compress_image_to_b64, image_to_desc, convert_to_jpg_b64, getdb, close_db, initdb
from PIL import Image 
from io import BytesIO
from openai import OpenAI, OpenAIError
from mysql.connector import errorcode



load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('APP_SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

AUTH_URL = os.getenv('AUTH_URL')
TOKEN_URL = os.getenv('TOKEN_URL')
API_BASE_URL = os.getenv('API_BASE_URL')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize database tables at startup
with app.app_context():
    initdb()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private ugc-image-upload'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args["error"]})

    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlistsform')

@app.route("/playlistsform")
def my_form():
    return render_template('form.html')
    
@app.route('/playlistsform', methods=['GET', 'POST'])
def get_playlist_info(): #getting playlist name and image (to create mood)
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    print(request.method)
    if request.method == 'POST':
        pl_name = request.form.get('playlist_name')
        pl_theme = request.form.get('playlist_theme')
        playlist_image = request.files.get('img')
    else:
        pl_name = request.form['playlist_name']
        pl_theme = request.form['playlist_theme']
        playlist_image = request.files['img']


    if not pl_name or not pl_theme or not playlist_image:
        flash('All fields are required, including an image. Please try again.')
        return redirect('/playlistsform')

    im = Image.open(playlist_image)

    img_str = convert_to_jpg_b64(im)

    sp = spotipy.Spotify(auth=session['access_token'], requests_timeout=30)
    user = sp.current_user()

    try:
        result1 = image_to_desc(img_str, OPENAI_API_KEY, pl_theme=pl_theme)
    except Exception as e:
        print(f"Failed to get image description: {e}")
        flash('Error generating image description. Please try again.')
        return redirect('/playlistsform')

    if result1 is None:
        flash('Failed to get image description from OpenAI.')
        return redirect('/playlistsform')

    session['playlist_image'] = result1
    session['pl_name'] = pl_name
    session['pl_theme'] = pl_theme

    playlist_desc = "Your curated "
    create_playlist_fun(sp, user['id'], pl_name, 'Test playlist created using python!')
    preplaylist = sp.user_playlists(user=user['id'])
    pplaylist = preplaylist['items'][0]['id']

    prmt = result1.split('$&$')[0]

    image = None

    try:
        image = generate_image(prmt)
    except OpenAIError as e:
        print(f'{e}')
            
    if image is None:
        sp.playlist_upload_cover_image(pplaylist, img_str)
    else:
        compressed_image_b64 = compress_image_to_b64(image, quality=75)
        i = 5
        while len(compressed_image_b64) >= 170000:
            compressed_image_b64 = compress_image_to_b64(image, quality=75 - i)
            i += 5

        sp.playlist_upload_cover_image(pplaylist, compressed_image_b64)
            
    preplaylist = sp.user_playlists(user=user['id'])
    pplaylist = preplaylist['items'][0]['id']

    img_url = preplaylist['items'][0]['images'][0]['url']

    connection = getdb()
    cursor = connection.cursor()

    try:
        cursor.execute(f"INSERT INTO accounts (accname) VALUES ('{user['id']}')")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:  # Handle duplicate entry error
            connection.rollback()
            print(f"Duplicate entry found for user ID: {user['id']}")
        else:
            raise  # Re-raise the exception if it's not a duplicate entry error
    # print(f"image url is : {img_url}")

    # print('--------')
    # print(pplaylist)
    # print(user['id'])
    # print(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    # print(prmt)

    prmt_escaped = prmt.replace("'", "''")
    try:
        cursor.execute(f"INSERT INTO playlists (playlistID, accname, pldate, prompt, image_url) VALUES ('{pplaylist}', '{user['id']}', '{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}', '{prmt_escaped}', '{img_url}')")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:  # Handle duplicate entry error
            connection.rollback()
            print(f"Duplicate entry found for user ID: {pplaylist}")
        else:
            raise  # Re-raise the exception if it's not a duplicate entry error


    connection.commit()
    cursor.close()

    return redirect('/playlists')

@app.route('/playlists', methods=['GET', 'POST'])
def create_playlist():
    pl_name = session['pl_name']
    pl_theme = session['pl_theme']

    sp = spotipy.Spotify(auth=session['access_token'])
    user = sp.current_user()

    response1 = session['playlist_image'].split('$&$')
    prompt = response1[0]
    # print('---------')
    # print(prompt)
    songlist = response1[1].split('&,')

    print(songlist)

    if len(songlist) == 1:
        songlist = response1[1].split('&),')

    #create_playlist_fun(sp, user['id'], pl_name, 'Test playlist created using python!')
    list_of_songs = []

    for songitem in songlist:
        songitem = songitem.replace("\n","").split(': ')
        song = songitem[0]
        artist = songitem[1]
        songsearch = sp.search(q=song)
        list_of_songs.append(songsearch['tracks']['items'][0]['uri'])
    # print(list_of_songs)

    preplaylist =sp.user_playlists(user=user['id'])
    #print(preplaylist['items'][0]['id'])
    pplaylist = preplaylist['items'][0]['id']
    session['plst_name'] = pplaylist
    sp.user_playlist_add_tracks(user = user['id'], playlist_id=pplaylist, tracks=list_of_songs)
    
    #print(f"\nPlaylist was created successfully.")
    return redirect('/curatedplaylist')

@app.route('/curatedplaylist', methods=['GET', 'POST'])
def display_curatedplaylist():
    #print(session['playlist_image'])
    #plst = f"https://open.spotify.com/embed/playlist/{session['plst_name']}?utm_source=generator"
    plst = f"https://open.spotify.com/embed/playlist/{session['plst_name']}?utm_source=generator&theme=0"
    
    return render_template('listpl.html', plst_url=plst)



@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'authorization_code',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data = req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        
        return redirect('/playlistsform')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port = 5001)