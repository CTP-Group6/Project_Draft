import sys
import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from mpl_toolkits import mplot3d

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import songrec
#TODO: 
# - Decorate
# - Organize
# - Distance selection implementation?
# - plotly events

CURRENT_THEME = "green"

st.set_page_config(
    page_title="WAVfinder",
    page_icon="👋",
    layout="centered",
    initial_sidebar_state='auto'
)



#User-specfic ID and SECRET, DONT PUSH WITH THIS
SPOTIPY_CLIENT_ID='538e939cf8ef4442a022c1c7f8b5188d'
SPOTIPY_CLIENT_SECRET='97e65146707242209cebcd4c76d09457'
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)



songs_data = pd.read_csv('preprocessed_songs.csv')
genre_matrix = pd.read_csv('preprocessed_matrix.csv').set_index('0')



#can use this same for selecting attributes of songs
st.title("WAV.finder")
st.write('Use the sidebar and dropdowns below to specify preferences, then hit the "Graph" button to visualize')



distance_choices = ['Very Far', 'Far', 'Neutral', 'Close', 'Very Close']
selected_distance = st.selectbox(
    label="Select Distance below",
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
    st.session_state.valence = st.slider("Valence", 0.000, 1.000, st.session_state.valence)


def update_sliders_based_on_track(track_features):
    if track_features:
        # Update the values of the sliders directly
        st.session_state.energy = track_features[0]['energy']
        st.session_state.danceability = track_features[0]['danceability']
        st.session_state.valence = track_features[0]['valence']
                    


# Extract unique genres from the matrix
available_genres = genre_matrix.index.tolist()

search_keyword = st.text_input(
    label = "Search for a Song"
)
button_clicked = st.button("Search")




with st.sidebar:
    selected_genre = st.selectbox(
        label="Select a Genre",
            options=genre_matrix.index.tolist()
    )
    if not selected_genre:
        st.warning("Please select a genre.")
    # Display the selected genre
    st.write(f"You selected genre: {selected_genre}")



# Now you can use selected_genre in your further logic



search_results = []
tracks = []
if search_keyword is not None and len(str(search_keyword)) > 0:
    st.write("Starting song search...")
    tracks = sp.search(q='track'+search_keyword,type='track')
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
        for track in tracks_list:
            search_results.append(track['name'] + " - By - " + track['artists'][0]['name'])



selected_track = None
track_id = None
selected_track_choice = None

selected_track = st.selectbox("Select your song/track: ", search_results)

if selected_track is not None and len(tracks) > 0:
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
        for track in tracks_list:
            str_temp = track['name'] + " - By - " + track['artists'][0]['name']
            if str_temp == selected_track:
                track_id = track['id']
                preview = track['preview_url']


    if track_id is not None:

        st.write("Please select track choice:")
        #song_features_button = st.button('Song Features')
        similar_songs_button = st.button('Similar Songs Recommendation')
        similar_consigned_button = st.button('Similar Song Consigned')  

        track_features  = sp.audio_features(track_id)
        track_info = sp.track(track_id)
        artists = track_info['artists']

        artist_id = artists[0]['id']
        artist_info = sp.artist(artist_id)
        artist_genres = artist_info['genres']

        #artist_genres_df = pd.DataFrame(artist_genres, columns=['genre'])
        chosen_track_features_df = pd.DataFrame(track_features, index=[0])
        song_name = track_info['name']
        chosen_track_features_df['track_name'] = song_name
        
        #chosen_song_name
        #chosen_track_name = pd.DataFrame(artist_info['name'])
        #chosen_track_features_df.append(chosen_track_name)
        #chosen_track_features_df


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


        if similar_songs_button:
            token = songrec.get_token(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
            similar_songs_json = songrec.get_track_recommendations(track_id,token)
            recommendation_list = similar_songs_json['tracks']
            recommendation_list_df = pd.DataFrame(recommendation_list)

            # Extracting artist information in a readable format
            recommendation_list_df['artists'] = recommendation_list_df['artists'].apply(lambda artists: ', '.join([artist['name'] for artist in artists]))

            # Displaying the DataFrame with selected columns
            st.write("Recommendations....")
            st.dataframe(recommendation_list_df[['name', 'artists', 'explicit', 'duration_ms', 'popularity']])


            graph_df = pd.DataFrame()

            for index, row in recommendation_list_df.iterrows():
                temp_track_id = row['id']
                temp_track_features = sp.audio_features(temp_track_id)
                temp_df = pd.DataFrame(temp_track_features, index=[0])

                # Include track name and audio preview URL from 'row' variable
                temp_df['track_name'] = row['name']
                temp_df['preview_url'] = row['preview_url']

                temp_features_df = temp_df.loc[:, ['track_name', 'acousticness', 'danceability', 'tempo', 'energy', 'valence', 'preview_url']]
                #st.dataframe(temp_features_df)
                graph_df = graph_df.append(temp_features_df, ignore_index=True)


            graph_df = graph_df.append(chosen_track_features_df, ignore_index=True)

            fig = px.scatter_3d(graph_df, x='tempo', y='energy', z='danceability', color='valence', size_max=18,
                            color_continuous_scale='aggrnyl', hover_name='track_name',
                            labels={'tempo': 'Tempo', 'energy': 'Energy', 'danceability': 'Danceability'})
        
            #selected_points = plotly_events(fig, click_event=True, hover_event=False)
        
            st.plotly_chart(fig)



        elif similar_consigned_button:
                    update_sliders_based_on_track(track_features)
                    selected_genre_songs = songrec.update_distance_selection(selected_distance, selected_genre, songs_data)

                    # Check if matching songs are found for the selected genre
                    if not selected_genre_songs.empty:
                        # Filter selected songs based on range criteria
                        recommendations = selected_genre_songs[
                            selected_genre_songs['energy'].between(st.session_state.energy - 0.1, st.session_state.energy + 0.1) &
                            selected_genre_songs['danceability'].between(st.session_state.danceability - 0.1, st.session_state.danceability + 0.1) &
                            selected_genre_songs['valence'].between(st.session_state.valence - 0.1, st.session_state.valence + 0.1)]

                        # Recommend top 5 matching songs
                        st.write("Top 5 Recommendations:")
                        st.dataframe(recommendations[['name', 'artists', 'genre','energy', 'danceability', 'valence']].head(10))
                        
                        st.write("Creating graph of similar songs...")

                        track_ids = selected_genre_songs['id'].tolist()[:20]
                        # Get track information for multiple tracks
                        tracks_info = sp.tracks(track_ids)
                        temp_features_df_list = []

                        for index, track in enumerate(tracks_info['tracks']):
                            if index >= 15:
                                break

                            temp_track_id = track['id']
                            temp_track_features = sp.audio_features(temp_track_id)
                            temp_df = pd.DataFrame(temp_track_features, index=[0])

                            # Include track name and audio preview URL from 'tracks_info_dict'
                            temp_df['track_name'] = track['name']
                            if temp_track_features and 'preview_url' in temp_track_features[0]:
                                temp_df['preview_url'] = temp_track_features[0]['preview_url']
                            else:
                                temp_df['preview_url'] = None  # or some default value

                            temp_features_df = temp_df.loc[:, ['track_name', 'energy', 'danceability', 'tempo', 'valence',  'preview_url']]
                            temp_features_df_list.append(temp_features_df)


                        graph_df = pd.concat(temp_features_df_list, ignore_index=True)

                        graph_df = graph_df.append(chosen_track_features_df, ignore_index=True)

                        fig = px.scatter_3d(graph_df, x='tempo', y='energy', z='danceability', color='valence', size_max=18,
                                            color_continuous_scale='aggrnyl', hover_name='track_name',
                                            labels={'tempo': 'Tempo', 'energy': 'Energy', 'danceability': 'Danceability'})
                        
                        #selected_points = plotly_events(fig, click_event=True, hover_event=False)             to implement
                        
                        st.plotly_chart(fig)



    else:
        st.write("Please select a track from the list")   

