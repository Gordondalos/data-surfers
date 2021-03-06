import pandas as pd
import requests
from bs4 import BeautifulSoup


def mb_parse_artists(page_limit: int) -> pd.DataFrame:
    artists_table = []
    for page in range(1, page_limit + 1):
        res = requests.get(
            "https://musicbrainz.org/area/1f1fc3a4-9500-39b8-9f10-f0a465557eef/artists?page={}".format(
                page
            )
        )
        soup = BeautifulSoup(res.text)
        artists = soup.find_all(role="row")

        for i in range(1, len(artists)):
            mb_id = artists[i].a["href"]
            name = artists[i].bdi.text
            band_type = artists[i].find_all("td", role="cell")[1].text
            artists_table.append([mb_id, name, band_type])

    df = pd.DataFrame(artists_table, columns=["musicbrainz_id", "artist", "type"])
    df = df.drop_duplicates(subset=["artist"])
    df["musicbrainz_id"] = df["musicbrainz_id"].apply(lambda x: x[8:])
    return df


if __name__ == "__main__":
    data = mb_parse_artists(145)
    data.to_csv("../data/intermediate/musicbrainz_artists.csv", index=False)
