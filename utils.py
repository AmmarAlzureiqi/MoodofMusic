import spotipy
import requests
import openai
import base64
import mysql.connector
import os
import time
import psycopg2
import transformers
from torch import no_grad
import torch.nn.functional as F
import numpy as np


from openai import OpenAI
from requests.exceptions import RequestException
from PIL import Image
from io import BytesIO
from flask import g
from psycopg2 import sql



def image_to_desc(base64_image, openai_key, pl_theme="None"):
    openai.api_key = openai_key

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    prompt_text = f"""
    Create a list of 20 songs for this playlist theme: {pl_theme}.
    The form of your response should be 'Description$&$List_of_songs', where List_of_songs is in this format ("song name": artist&).
    """
    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                can you create a list of 20 songs that would match the setting portrayed in this image and/or to set the vibe 
                portrayed by this image use it to select recommendations.
                Also make sure to favour songs that are higher rated and more popular. I need a minimum of 15 songs.
                I just want you to list the results in this format ("song name": artist&), separated by commas and nothing 
                else in your response. Additionally give me a little description of the image as a prompt to pass on to 
                DALL-E to make a cartoony version of the prompt as a playlist cover (put this part at the beginning of your 
                response and separate from the list using $&$). 
                Just a reminder: the form of your response should be 'Description$&$List_of_songs', where List_of_songs is in this format ("song name": artist&)
                """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response_data.get('error', {}).get('message', 'Unknown error')}")
    
    res1 = response_data['choices'][0]['message']['content']
    print(response.json())
    return res1

def image_to_desc2(base64_image, openai_key, pl_theme="None"):
    openai.api_key = openai_key

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        Can you describe the image given, so that the decription can be later used to make cartoon version for a spotify playlist cover.
                        Don't make your response too long, and only include the description in your response.
                """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response_data.get('error', {}).get('message', 'Unknown error')}")
    
    res1 = response_data['choices'][0]['message']['content']
    return res1

def create_playlist_fun(sp, username, playlist_name, playlist_description):
    playlists = sp.user_playlist_create(username, playlist_name, description = playlist_description, public=True)

def generate_image(prmt):
    client = openai.OpenAI()  # Assuming this is the correct initialization for the OpenAI client

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A cartoon picture of this description: {prmt}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        if not response or not response.data:
            print("No data received from OpenAI API")
            return None

        img_url = response.data[0].url
        if not img_url:
            print("No URL found in the response data")
            return None

        # Log the URL for debugging purposes
        print(f"Image URL: {img_url}")

        img_response = requests.get(img_url)
        img_response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        image = Image.open(BytesIO(img_response.content))

        return image

    except RequestException as e:
        print(f"Error fetching image from URL: {e}")
        return None
    except openai.error.OpenAIAPIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def compress_image(image, output_path, quality=85):
    image.save(output_path, format="JPEG", quality=quality)

def compress_image_to_b64(image, quality=85):
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    image_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return image_b64

def convert_to_jpg_b64(img):
    rgb_im = img.convert("RGB")
    rgb_im = rgb_im.resize((264, 264), Image.LANCZOS)
    
    buffered = BytesIO()
    rgb_im.save(buffered, format="JPEG", quality=85)

    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return img_str


# def getdb():
#     if 'db' not in g or not g.db.is_connected():
#         g.db = mysql.connector.connect(
#             host=os.getenv('MYSQL_HOST', 'localhost'),  # default to 'mysql_db' for Docker setup
#             user=os.getenv('MYSQL_USER', 'root'),
#             password=os.getenv('MYSQL_PASSWORD', 'test_root'),
#             database=os.getenv('MYSQL_DB', 'moodofmusic')
#         )
#     return g.db

# def close_db(e=None):
#     db = g.pop('db', None)

#     if db is not None and db.is_connected():
#         db.close()


def getdb():
    if 'db' not in g or g.db.closed:
        g.db = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'your_password'),
            dbname=os.getenv('POSTGRES_DB', 'moodofmusic')
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def insert_account(cursor, user_id):
    try:
        cursor.execute(
            sql.SQL("INSERT INTO accounts (accname) VALUES (%s)"),
            [user_id]
        )
    except psycopg2.IntegrityError as err:
        if err.pgcode == '23505':  # Duplicate entry error code for PostgreSQL
            print(f"Duplicate entry found for user ID: {user_id}")
            cursor.connection.rollback()
        else:
            raise

def insert_playlist(cursor, pplaylist, pl_name, pl_theme, user_id, prompt, img_url):
    try:
        cursor.execute(
            sql.SQL("""
                INSERT INTO playlists (playlistID, plname, pltheme, accname, pldate, prompt, image_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """),
            [pplaylist, pl_name, pl_theme, user_id, datetime.today().strftime('%Y-%m-%d %H:%M:%S'), prompt.replace("'", "''"), img_url]
        )
    except psycopg2.IntegrityError as err:
        if err.pgcode == '23505':  # Duplicate entry error code for PostgreSQL
            print(f"Duplicate entry found for playlist ID: {pplaylist}")
            cursor.connection.rollback()
        else:
            raise

def initdb():
    db = getdb()
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        accname VARCHAR(255) NOT NULL PRIMARY KEY
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        playlistID VARCHAR(100) NOT NULL,
        plname VARCHAR(255),
        pltheme VARCHAR(255),
        accname VARCHAR(255) NOT NULL,
        pldate TIMESTAMP,
        prompt TEXT,
        image_url VARCHAR(512),
        PRIMARY KEY (playlistID),
        FOREIGN KEY (accname) REFERENCES accounts(accname)
    )
    ''')
    db.commit()
    cursor.close()



# def getdb():
#     if 'db' not in g:
#         g.db = None
#         attempts = 0
#         while g.db is None and attempts < 5:
#             try:
#                 g.db = mysql.connector.connect(
#                     host='mysql_db',
#                     user='root',
#                     password='test_root',
#                     database='moodofmusic'
#                 )
#             except mysql.connector.Error as err:
#                 attempts += 1
#                 print(f"Error: {err}. Retrying in 5 seconds...")
#                 time.sleep(5)
#     if g.db is None:
#         raise ConnectionError("Failed to connect to the database after several attempts.")
#     print('Database Connected')
#     return g.db

# def initdb():
#     db = getdb()
#     cursor = db.cursor()
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS accounts (
#         accname VARCHAR(255) NOT NULL PRIMARY KEY
#     )
#     ''')
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS playlists (
#         playlistID VARCHAR(100) NOT NULL,
#         accname VARCHAR(255) NOT NULL,
#         pldate DATE,
#         prompt VARCHAR(10000),
#         image_url VARCHAR(512),
#         PRIMARY KEY (playlistID)
#     )
#     ''')
#     db.commit()
#     cursor.close()

def get_recommendations(sp, genres, valence, energy, danceability, tempo, loudness, acousticness):
    recommendations = sp.recommendations(limit=20, seed_genres=genres, target_valence=valence, target_energy=energy, target_danceability=danceability, target_tempo=tempo, target_loudness=loudness, target_acousticness=acousticness)['tracks']
    return recommendations

def get_recommendations_artist(sp,artists):
    recommendations = sp.recommendations(limit=20, seed_artists=artists)['tracks']
    return recommendations

def get_top_artists(sp):
    top_artists = sp.current_user_top_artists(limit=5, time_range="medium_term")
    artsts=[]
    for artist in top_artists["items"]:
        artsts.append(artist["id"])
    return artsts

def emotion_cat2dim(category: str) -> tuple[float, float, float, float, float]:
    if category == "amusement":
        valence, energ = 0.55, 0.1
        danceability, tempo, loudness, acousticness = 0.7, 150, -8, 0.2
    elif category == "anger":
        valence, energ = -0.4, 0.8
        danceability, tempo, loudness, acousticness = 0.6, 170, -7, 0.1
    elif category == "awe":
        valence, energ = 0.3, 0.9
        danceability, tempo, loudness, acousticness = 0.8, 140, -10, 0.3
    elif category == "contentment":
        valence, energ = 0.9, -0.3
        danceability, tempo, loudness, acousticness = 0.5, 130, -9, 0.4
    elif category == "disgust":
        valence, energ = -0.7, 0.5
        danceability, tempo, loudness, acousticness = 0.4, 160, -6, 0.05
    elif category == "excitement":
        valence, energ = 0.7, 0.7
        danceability, tempo, loudness, acousticness = 0.9, 180, -5, 0.15
    elif category == "fear":
        valence, energ = -0.1, 0.7
        danceability, tempo, loudness, acousticness = 0.3, 150, -11, 0.25
    elif category == "sadness":
        valence, energ = -0.8, -0.7
        danceability, tempo, loudness, acousticness = 0.2, 120, -12, 0.1
    return (valence/1.7 + 0.85, energ/1.6 + 0.8, danceability, tempo, loudness, acousticness)

def get_song_params(image):
        
    # Emotional categories
    idx2cat = [
        "amusement",
        "anger",
        "awe",
        "contentment",
        "disgust",
        "excitement",
        "fear",
        "sadness",
    ]

    image_processor = transformers.ViTImageProcessor.from_pretrained("google/vit-large-patch16-224")
    model = transformers.ViTForImageClassification.from_pretrained("google/vit-large-patch16-224")

    # Inference with the ViT model
    with no_grad():
        # Get logits from the ViT model
        cat_idx = model(**image_processor(image, return_tensors="pt")).logits
        
        # Calculate softmax probabilities
        probs = F.softmax(cat_idx)[0, :len(idx2cat)]
        
        # Calculate emotion values based on categories
        emotion = np.zeros(6, dtype=np.float32)  
        for idx, cat in enumerate(idx2cat):
            valence, energ, danceability, tempo, loudness, acousticness = emotion_cat2dim(cat)
            emotion[0] += valence * probs[idx].item()
            emotion[1] += energ * probs[idx].item()
            emotion[2] += danceability * probs[idx].item()
            emotion[3] += tempo * probs[idx].item()
            emotion[4] += loudness * probs[idx].item()
            emotion[5] += acousticness * probs[idx].item()

        return emotion

