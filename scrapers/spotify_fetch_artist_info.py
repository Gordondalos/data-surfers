from typing import Any, Dict, List, Optional

import pandas as pd
import spotipy
import streamlit as st
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from scrapers.st_utils import StProgress

st.title("Spotify artist info downloader")

DATA_URL = "../data/intermediate/musicbrainz_artists.csv"


@st.cache
def load_data(nrows: int) -> pd.DataFrame:
    data = pd.read_csv(DATA_URL, nrows=nrows)
    return data


st.subheader(len(pd.read_csv(DATA_URL)))

data_load_state = st.text("Loading data...")
data = load_data(10000)
data_load_state.text("Data loaded!")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data.head())


@st.cache(allow_output_mutation=True)
def spotify_client() -> spotipy.client.Spotify:
    load_dotenv()
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials())


def find_artist(artist_name: str) -> Optional[Dict[str, Any]]:
    sp = spotify_client()

    results = sp.search(q=artist_name, limit=20, type="artist")
    # todo тут должны быть какие-то эвристики для определения,
    # действительно ли нашелся именно тот артист, которого мы искали?

    # todo кэшировать полный ответ апишки

    if len(results["artists"]["items"]) == 0:
        return None

    return results["artists"]["items"][0]


def sp_artist_to_ds_artists(sp_artist: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if sp_artist is None:
        return {
            "spotify_id": "",
            "followers": 0,
            "genres": [],
            "popularity": 0,
        }

    return {
        "spotify_id": sp_artist["id"],
        "followers": sp_artist["followers"]["total"],
        "genres": sp_artist["genres"],
        "popularity": sp_artist["popularity"],
    }


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_artists_info(artists_names: List[str]) -> pd.DataFrame:
    spotify_artists_data = {
        "spotify_id": [],
        "followers": [],
        "genres": [],
        "popularity": [],
    }

    for artist_name in StProgress(
        artists_names, title=f"Обкачиваем {len(artists_names)} артистов"
    ):
        try:
            sp_artist = find_artist(artist_name)
            spotify_artist_data = sp_artist_to_ds_artists(sp_artist)

            for k in spotify_artist_data.keys():
                spotify_artists_data[k].append(spotify_artist_data[k])

        except Exception as e:
            st.write(e)
            st.text("Some errors on processing artists on " + artist_name)
            break

    return pd.DataFrame(spotify_artists_data)


find_artist_name = st.text_input("Поиск артиста", "")
st.text(
    "Для классиков есть проблема:\nесли искать по ФИО, то, например `Сергей Васильевич Рахманинов` поиск найти не может,\nа `Рахманинов` может"
)
if find_artist_name != "":
    st.write(find_artist(find_artist_name))

spotify_artists_data = get_artists_info(data["artist"])
st.write(spotify_artists_data)


st.subheader("Итого")
result_artist_info_df = pd.concat((data, spotify_artists_data), axis=1)
st.write(result_artist_info_df)

result_artist_info_df.to_csv("../data/artists.csv", index=False)

st.subheader("Кол-во артистов, по которым смогли найти что-то в поиске")
st.write(len(result_artist_info_df[result_artist_info_df["followers"] > 0]))
