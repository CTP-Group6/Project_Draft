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

st.set_page_config(
    page_title="Hello",
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


#can use this same for selecting attributes of songs
st.header('Test for Spotify API')
distancechoices = ['Very Far', 'far', 'Close', 'Very Close']
genrechoices = ['Pop', 'Rock', 'Hip Hop', 'Country']

Distance = st.selectbox(
    label = "Select Distance below",
    options = distancechoices
)

Genre = st.selectbox(
    label = "Select Genre Below",
    options = genrechoices
)

search_keyword = st.text_input(
    label = "Search for a Song"
)

button_clicked = st.button("Search")

search_results = []
tracks = []
if search_keyword is not None and len(str(search_keyword)) > 0:
    st.write("Searching...")
    tracks = sp.search(q='track'+search_keyword,type='track')
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
        for track in tracks_list:
            search_results.append(track['name'] + " - By - " + track['artists'][0]['name'])



selected_track = None
selected_track = st.selectbox("Select your song/track: ", search_results)

if selected_track is not None and len(tracks) > 0:
    tracks_list = tracks['tracks']['items']
    track_id = None
    if len(tracks_list) > 0:
        for track in tracks_list:
            str_temp = track['name'] + " - By - " + track['artists'][0]['name']
            if str_temp == selected_track:
                track_id = track['id']
                preview = track['preview_url']
               
    selected_track_choice = None            
    if track_id is not None:
        track_choices = ['Song Features', 'Similar Songs Recommendation']
        selected_track_choice = st.sidebar.selectbox('Please select track choice: ', track_choices)    

        if selected_track_choice == 'Song Features':
            track_features  = sp.audio_features(track_id) 
            df = pd.DataFrame(track_features, index=[0])
            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'tempo', 'valence']]
            st.dataframe(df_features)
            if preview is not None:
                st.audio(preview, format="audio/mp3")

        elif selected_track_choice == 'Similar Songs Recommendation':
            token = songrec.get_token(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
            similar_songs_json = songrec.get_track_recommendations(track_id, token)
            recommendation_list = similar_songs_json['tracks']
            recommendation_list_df = pd.DataFrame(recommendation_list)
            #st.dataframe(recommendation_list_df)
            recommendation_df = recommendation_list_df[['name','artists', 'explicit', 'duration_ms', 'popularity','preview_url']]
            st.write("Recommendations....")
            st.dataframe(recommendation_df)
            lulaudio = recommendation_df.iloc[0]
            st.audio(lulaudio['preview_url'], format="audio/mp3")
            #songrec.song_recommendation_vis(recommendation_df)

    else:
        st.write("Please select a track from the list")   



if st.button("Graph"):
    if selected_track_choice == 'Similar Songs Recommendation':
        st.write("Creating graph based off your chosen song")
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
        st.write("Creating graph based off features of your chosen song")
        graph_df = df_features

        temp_features_df = graph_df.loc[: ,['acousticness', 'danceability', 'tempo', 'energy']]
        graph_df = graph_df.append(temp_features_df)

        fig = px.scatter_3d(graph_df, x='tempo', y='energy', z='danceability', color='acousticness', size_max=18,
                    color_continuous_scale='aggrnyl', labels={'tempo': 'Tempo', 'energy': 'Energy', 'danceability': 'Danceability'})
        st.plotly_chart(fig)



with st.sidebar: # creates side bar
    #TODO: variables instead of preset energy, tempo...
    Energy = st.slider(
        "Energy",0.000,1.000,.500
        )
    Tempo = st.slider(
        "Tempo",0.000,1.000,.500
        )
    Danceability = st.slider(
        "Danceability",0.000,1.000,.500
        )