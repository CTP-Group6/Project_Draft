import requests
import base64
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
from PIL import Image

def get_token(clientId,clientSecret):
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}
    message = f"{clientId}:{clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')
    headers['Authorization'] = "Basic " + base64Message
    data['grant_type'] = "client_credentials"
    r = requests.post(url, headers=headers, data=data)
    token = r.json()['access_token']
    return token

def get_track_recommendations(seed_tracks,token):
    limit = 10
    recUrl = f"https://api.spotify.com/v1/recommendations?limit={limit}&seed_tracks={seed_tracks}"

    headers = {
        "Authorization": "Bearer " + token
    }

    res = requests.get(url=recUrl, headers=headers)
    return res.json()

genre_matrix = pd.read_csv('preprocessed_matrix.csv').set_index('0')
songs_data = pd.read_csv('processed_songs.csv')
def update_distance_selection(selected_distance, selected_genre, songs_data):
    distance_ranges = {
        'Very Far': slice(-700, -1),
        'Far': slice(-1300, -700),
        'Neutral': slice(800, 1600),
        'Close': slice(300, 700),
        'Very Close': slice(0, 100),
    }

    if selected_distance not in distance_ranges:
        return pd.DataFrame()  # or handle unexpected cases

    genre_distances = genre_matrix.loc[selected_genre]
    sorted_genres = genre_distances.sort_values()
    updated_genres = sorted_genres.iloc[distance_ranges[selected_distance]]

    # Filter songs based on the updated genres
    selected_genre_songs = songs_data[songs_data['genre'].isin(updated_genres.index)]

    return selected_genre_songs
