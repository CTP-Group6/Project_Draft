import sys
import ast
import streamlit as st

import pandas as pd

import plotly.express as px
from mpl_toolkits import mplot3d
from streamlit_plotly_events import plotly_events

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import songrec

#py -m streamlit run "c:/Users/henry/project folder/Project_Draft/Spotifytest.py"
#import polarplot
#import songrecommendations

CURRENT_THEME = "green"

st.set_page_config(
    page_title="wav.finder",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state='auto'
)

# Spotify API credentials
SPOTIPY_CLIENT_ID='insert_client_id_here'
SPOTIPY_CLIENT_SECRET='insert_secret_here'
#SPOTIPY_REDIRECT_URI='WavFinder.streamlit.app'
songs_data = pd.read_csv('processed_songs.csv')
genre_matrix = pd.read_csv('preprocessed_matrix.csv').set_index('0')
#sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
#redirect_uri=REDIRECT_URI,scope=SCOPE, show_dialog=True, cache_path=CACHE)

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
st.title("🚀Wav.finder")

distance_choices = ['Very Far', 'Far', 'Neutral', 'Close', 'Very Close']
selected_distance = st.sidebar.selectbox(
    label="How far do you want to go?",
    options=distance_choices,
    index=2  # Default to 'Neutral'
)
with st.sidebar:
    if 'energy' not in st.session_state:
        st.session_state.energy = 0.5
    if 'danceability' not in st.session_state:
        st.session_state.danceability = 0.5
    if 'valence' not in st.session_state:
        st.session_state.valence = 0.5

    st.session_state.energy = st.slider("Energy", 0.000, 1.000, st.session_state.energy)
    st.session_state.danceability = st.slider("Danceability", 0.000, 1.000, st.session_state.danceability)
    st.session_state.valence = st.slider("Emotion", 0.000, 1.000, st.session_state.valence)

def update_sliders_based_on_track(track_features):
    if track_features:
        # Update the values of the sliders directly
        st.session_state.energy = track_features[0]['energy']
        st.session_state.danceability = track_features[0]['danceability']
        st.session_state.valence = track_features[0]['valence']

# Extract unique genres from the matrix
available_genres = genre_matrix.index.tolist()

# Now you can use selected_genre in your further logic
search_keyword = st.text_input(
    label = "Search for a Song"
)
button_clicked = st.button("Search")

search_results = []
tracks = []

if search_keyword is not None and len(str(search_keyword)) > 0:
    st.write("Starting song search...")

    try:
        # Add a space between 'track' and the search keyword
        tracks = sp.search(q='track ' + search_keyword, type='track', limit=10)
        tracks_list = tracks['tracks']['items']

        if tracks_list:
            for track in tracks_list:
                search_results.append(track['name'] + " - By - " + track['artists'][0]['name'])
    except Exception as e:
        st.write("An error occurred while searching for songs: " + str(e))


selected_track = None
track_id = None
track_features = None
update_sliders_based_on_track(track_features)

selected_track = st.selectbox("Select your song/track: ", search_results)

if selected_track is not None and len(tracks) > 0:
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
        for track in tracks_list:
            str_temp = track['name'] + " - By - " + track['artists'][0]['name']
            if str_temp == selected_track:
                track_id = track['id']
                preview = track['preview_url']

        st.write("Please select track choice:")
        similar_consigned_button = st.button('Launch Song recommendations')  

        track_features  = sp.audio_features(track_id)
        track_info = sp.track(track_id)
        artists = track_info['artists']

        artist_id = artists[0]['id']
        artist_info = sp.artist(artist_id)
        artist_genres = artist_info['genres']

        #artist_genres_df = pd.DataFrame(artist_genres, columns=['genre'])

        with st.sidebar:
            selected_genre = st.selectbox(
                label="Select a Genre",
                options=artist_genres
            )
            if not selected_genre:
                st.warning("Please select a genre.")
            # Display the selected genre
            st.write(f"You selected genre: {selected_genre}")

        df = pd.DataFrame(track_features, index=[0])
        df_features = df.loc[: ,['energy', 'danceability', 'valence']]
        st.dataframe(df_features)
        
        if 'previous_track_id' not in st.session_state or st.session_state.previous_track_id != track_id:
            st.session_state.previous_track_id = track_id
            update_sliders_based_on_track(track_features)

        if preview is not None:
            st.audio(preview, format="audio/mp3")


        if similar_consigned_button:
                    
                    selected_genre_songs = songrec.update_distance_selection(selected_distance, selected_genre, songs_data)
                    # Check if matching songs are found for the selected genre
                    if not selected_genre_songs.empty:
                        # Filter selected songs based on range criteria
                        recommendations = selected_genre_songs[
                            selected_genre_songs['energy'].between(st.session_state.energy - 0.1, st.session_state.energy + 0.1) &
                            selected_genre_songs['danceability'].between(st.session_state.danceability - 0.1, st.session_state.danceability + 0.1) &
                            selected_genre_songs['valence'].between(st.session_state.valence - 0.1, st.session_state.valence + 0.1)
                            ]
                        # Recommend top 5 matching songs
                        recommendations = recommendations.head(20)
                        recommendations['artists'] = recommendations['artists'].apply(ast.literal_eval)

                        # Extract the first artist from the 'Artists' column
                        recommendations['firstartist'] = recommendations['artists'].apply(lambda x: x[0] if x else '')

                        st.write("Top 5 Recommendations:")

                        recommendations = recommendations.rename(columns={
                        'name': 'Track Name',
                        'firstartist': 'Primary Artist',
                        'genre': 'Genre',
                        'energy': 'Energy Level',
                        'danceability': 'Danceability',
                        'valence': 'Emotion'
                        })

                        st.dataframe(recommendations[['Track Name', 'Primary Artist', 'Genre', 'Energy Level', 'Danceability', 'Emotion']].head(10))
                        
                        st.write("Creating graph of similar songs...")

                        track_ids = recommendations['id'].tolist()[:20]

                        # Get track information for multiple tracks
                        tracks_info = sp.tracks(track_ids)



                        fig = px.scatter_3d(recommendations, x='Energy Level', y='Danceability', z='Emotion', color='Genre', size_max=18,
                                            color_continuous_scale='aggrnyl', hover_name='Track Name', text='Track Name')
                        #color by genre, make the primary song middle song and make it stand out. Song similarity
                        selected_points = plotly_events(fig, click_event=True, hover_event=False)
                        if selected_points and 'points' in selected_points and selected_points['points']:
                            # Get the track ID of the clicked point
                            clicked_track_id = selected_points['points'][0]['id']

                            # Update the spotify_embed_html string with the clicked track ID
                            spotify_embed_html = f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{clicked_track_id}?utm_source=generator"width="100%" height="440" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
                            st.markdown(spotify_embed_html,unsafe_allow_html=True)
                        st.plotly_chart(fig)
                        





    else:
        st.write("Please select a track from the list")
