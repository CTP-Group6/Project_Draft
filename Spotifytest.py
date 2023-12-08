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
# - Distance selection implementation
# - 

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



with st.sidebar:
    energy_placeholder = st.empty()
    danceability_placeholder = st.empty()
    valence_placeholder = st.empty()

with st.sidebar:
    energy = energy_placeholder.slider("Energy", 0.000, 1.000, .5)
    danceability = danceability_placeholder.slider("Danceability", 0.000, 1.000, .5)
    valence = valence_placeholder.slider("Valence", 0.000, 1.000, .5)

distance_choices = ['Very Far', 'Far', 'Neutral', 'Close', 'Very Close']

selected_distance = st.selectbox(
    label="Select Distance below",
    options=distance_choices,
    index=2  # Default to 'Neutral'
)
session_state = st.session_state



def update_sliders_based_on_track(track_features):
                if track_features:
                    with st.sidebar:
                        energy_placeholder.slider("Energy", 0.000, 1.000, track_features[0]['energy'])
                        danceability_placeholder.slider("Danceability", 0.000, 1.000, track_features[0]['danceability'])
                        valence_placeholder.slider("Valence", 0.000, 1.000, track_features[0]['valence'])
# Extract unique genres from the matrix
available_genres = genre_matrix.index.tolist()



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
search_keyword = st.text_input(
    label = "Search for a Song"
)

button_clicked = st.button("Search")

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
        track_choices = ['Similar Songs Recommendation', 'Song Features']
        selected_track_choice = st.sidebar.selectbox('Please select track choice: ', track_choices)    

        track_info = sp.track(track_id)
        artists = track_info['artists']

        #Song Features option
        if selected_track_choice == 'Song Features': 
            #track_features  = sp.audio_features(track_id) 
            #df = pd.DataFrame(track_features, index=[0])
            #df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'tempo', 'valence']]
            #st.dataframe(df_features)
            #if preview is not None:
            #    st.audio(preview, format="audio/mp3")

            artist_id = artists[0]['id']
            artist_info = sp.artist(artist_id)
            artist_genres = artist_info['genres']

            # Display genres
            if artist_genres:
                genre_string = ', '.join(artist_genres)
                st.write(f"Genres for the artist: {genre_string}")
            else:
                st.write("No genre information available for this artist.")
            
            track_features  = sp.audio_features(track_id)
            df = pd.DataFrame(track_features, index=[0])
            df_features = df.loc[: ,['energy', 'danceability', 'valence']]
            st.dataframe(df_features)
            update_sliders_based_on_track(track_features)

            if preview is not None:
                st.audio(preview, format="audio/mp3")


        #Similar Songs option
        elif selected_track_choice == 'Similar Songs Recommendation':
            token = songrec.get_token(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
            similar_songs_json = songrec.get_track_recommendations(track_id, token)
            recommendation_list = similar_songs_json['tracks']
            recommendation_list_df = pd.DataFrame(recommendation_list)
            #st.dataframe(recommendation_list_df)

            recommendation_list_df['artists'] = recommendation_list_df['artists'].apply(lambda artists: ', '.join([artist['name'] for artist in artists]))
            
            st.write("Recommendations:")
            st.dataframe(recommendation_list_df[['name', 'artists', 'explicit', 'duration_ms', 'popularity']])

            # Playing the first track's preview
            if not recommendation_list_df.empty:
                first_track = recommendation_list_df.iloc[0]
                if first_track['preview_url'] is not None:
                    st.audio(first_track['preview_url'], format="audio/mp3")

        elif selected_track_choice == 'Similar song consigned':
                    selected_genre_songs = songrec.update_distance_selection(selected_distance, selected_genre, songs_data)

                    # Check if matching songs are found for the selected genre
                    if not selected_genre_songs.empty:
                        # Filter selected songs based on range criteria
                        recommendations = selected_genre_songs[
                            selected_genre_songs['Energy'].between(energy - 0.1, energy + 0.1) &
                            selected_genre_songs['Dancebility'].between(danceability - 0.1, danceability + 0.1) &
                            selected_genre_songs['Valence'].between(valence - 0.1, valence + 0.1)
                        ]

                        # Recommend top 5 matching songs
                        st.write("Top 5 Recommendations:")
                        st.write(recommendations[['Name', 'Artists', 'Genre', 'Danceability', 'Energy', 'Valence']].head(5))


    else:
        st.write("Please select a track from the list")   



if st.button("Graph"):
    if selected_track_choice == 'Similar Songs Recommendation':
        st.write("Creating graph of similar songs...")
    #chosen_song_df = recommendation_df
   # graph_df = chosen_song_df.append(recommendation_list_df, ignore_index=True)
    #st.dataframe(recommendation_list_df)
        graph_df = pd.DataFrame()
        #st.dataframe(recommendation_list_df)

        for index, row in recommendation_list_df.iterrows():
            temp_track_id = row['id']
            temp_track_features  = sp.audio_features(temp_track_id) 
            temp_df = pd.DataFrame(temp_track_features, index=[0])
            temp_features_df = temp_df.loc[: ,['acousticness', 'danceability', 'tempo', 'energy']]
            graph_df = graph_df.append(temp_features_df)

        fig = px.scatter_3d(graph_df, x='tempo', y='energy', z='danceability', color='acousticness', size_max=18,
                    color_continuous_scale='aggrnyl', labels={'tempo': 'Tempo', 'energy': 'Energy', 'danceability': 'Danceability'})
        st.plotly_chart(fig)

    elif selected_track_choice == 'Song Features':
        st.write("Creating graph based off features of your chosen song...")
        graph_df = df_features

        temp_features_df = graph_df.loc[: ,['acousticness', 'danceability', 'tempo', 'energy']]
        graph_df = graph_df.append(temp_features_df)

        fig = px.scatter_3d(graph_df, x='tempo', y='energy', z='danceability', color='acousticness', size_max=18,
                    color_continuous_scale='aggrnyl', labels={'tempo': 'Tempo', 'energy': 'Energy', 'danceability': 'Danceability'})
        st.plotly_chart(fig)


