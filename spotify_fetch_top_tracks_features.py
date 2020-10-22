import streamlit as st
import pandas as pd
import numpy as np

from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from st_utils import StProgress

st.title('Spotify tracks features downloader')

DATA_URL = ('./artist_top_tracks.csv')


def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, )
    return data


data_load_state = st.text('Loading data...')
data = load_data(1000)

data_load_state.text(f"Loaded {len(data)} not null artists")

st.subheader('Raw data, len: ' + str(len(data)))
st.write(data['spotify_id'].head())


@st.cache(allow_output_mutation=True)
def spotify_client():
    load_dotenv()
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials())


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def track_features(sp_track_ids):
    sp = spotify_client()

    results = sp.audio_features(tracks=sp_track_ids)

    return results


st.subheader('Фичи трека по sp_id')
sp_track_id = st.text_input('', '')
if sp_track_id != '':
    st.write(track_features(sp_track_id))

def get_tracks_features(sp_tracks_ids):

    batch_size = 10

    audio_features = ["key",
                      "mode",
                      "time_signature",
                      "acousticness",
                      "danceability",
                      "energy",
                      "instrumentalness",
                      "liveness",
                      "loudness",
                      "speechiness",
                      "valence",
                      "tempo",
                      ]
    sp_tracks_features = { k: [] for k in audio_features }
    for i in StProgress(range(0, len(sp_tracks_ids), batch_size), title=f"Обкачиваем {len(sp_tracks_ids)} артистов"):

        try:
            sp_tracks_ids_batch = sp_tracks_ids[i:min(i+batch_size, len(sp_tracks_ids))]
            tracks_features_list = track_features(sp_tracks_ids_batch)
            for tr in tracks_features_list:
                for feature_name in audio_features:
                    sp_tracks_features[feature_name].append(tr[feature_name])

        except Exception as e:
            st.write(e)
            st.text("Some errors on processing artists on i=" + i)
            break

    return pd.DataFrame(sp_tracks_features)


sp_tracks_features = get_tracks_features(data['spotify_id'])

st.subheader("Итого")

sp_tracks_features = pd.concat( (data, sp_tracks_features), axis=1)

st.write(sp_tracks_features.head(50))

sp_tracks_features.to_csv("artist_top_tracks_with_features.csv", index=False)

st.subheader(f"Кол-во треков: {len(sp_tracks_features)}")