import spotipy
import requests
import openai
import base64
import mysql.connector
import os
import time

from openai import OpenAI
from PIL import Image
from io import BytesIO
from flask import g



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
    #print(response.json())
    return res1

    
# def image_to_desc1(base64_image, openai_key, pl_theme="None"):
#     openai.api_key = openai_key

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {openai.api_key}"
#     }

#     payload = {
#         "model": "gpt-4-vision-preview",
#         "messages": [
#             {
#                 "role": "user",
#                 "content":  f"""
#     Create a list of 20 songs for this playlist theme: {pl_theme}.
#     The form of your response should be 'Description$&$List_of_songs', where List_of_songs is in this format ("song name": artist&).
#     """
#                 # "content": f"""
#                 # can you create a list of 20 songs that would match the setting portrayed in this image and/or to set the vibe 
#                 # portrayed by this image use it to select recommendations.
#                 # Also make sure to favour songs that are higher rated and more popular. I need a minimum of 15 songs.
#                 # I just want you to list the results in this format ("song name": artist&), separated by commas and nothing 
#                 # else in your response. Additionally give me a little description of the image as a prompt to pass on to 
#                 # DALL-E to make a cartoony version of the prompt as a playlist cover (put this part at the beginning of your 
#                 # response and separate from the list using $&$). 
#                 # Just a reminder: the form of your response should be 'Description$&$List_of_songs', where List_of_songs is in this format ("song name": artist&)
#                 # """
#             },
#             {
#                 "role": "user",
#                 "content": f"data:image/jpeg;base64,{base64_image}"
#             }
#         ],
#         "max_tokens": 500
#     }

#     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
#     print(response.json())  # For debugging
#     try:
#         res1 = response.json()['choices'][0]['message']['content']
#         return res1
#     except KeyError:
#         print("KeyError: 'choices' not found in the response.")
#         return None


def create_playlist_fun(sp, username, playlist_name, playlist_description):
    playlists = sp.user_playlist_create(username, playlist_name, description = playlist_description, public=True)

def generate_image(prmt):
  client = OpenAI()

  response = client.images.generate(
    model="dall-e-3",
    prompt=f"A cartoon picture of this description: {prmt}",
    size="1024x1024",
    quality="standard",
    n=1,
  )
  img_url = response.data[0].url
  response = requests.get(img_url)
  image = Image.open(BytesIO(response.content))

  return image

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
#             host=os.getenv('MYSQL_HOST', 'mysql_db'),  # default to 'mysql_db' for Docker setup
#             user=os.getenv('MYSQL_USER', 'root'),
#             password=os.getenv('MYSQL_PASSWORD', 'test_root'),
#             database=os.getenv('MYSQL_DB', 'moodofmusic')
#         )
#     return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None and db.is_connected():
        db.close()

def getdb():
    if 'db' not in g:
        g.db = None
        attempts = 0
        while g.db is None and attempts < 5:
            try:
                g.db = mysql.connector.connect(
                    host='mysql_db',
                    user='root',
                    password='test_root',
                    database='moodofmusic'
                )
            except mysql.connector.Error as err:
                attempts += 1
                print(f"Error: {err}. Retrying in 5 seconds...")
                time.sleep(5)
    if g.db is None:
        raise ConnectionError("Failed to connect to the database after several attempts.")
    print('Database Connected')
    return g.db

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
        accname VARCHAR(255) NOT NULL,
        pldate DATE,
        prompt VARCHAR(10000),
        image_url VARCHAR(512),
        PRIMARY KEY (playlistID)
    )
    ''')
    db.commit()
    cursor.close()