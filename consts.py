import pandas as pd
import requests
import bs4

import scrap

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYW5kcmV5ZGVuIiwiYSI6ImNqbmhwdGlkMjBhYzQzanJzbTM3NzdobW8ifQ.ZR_vrBuTDB1-byVDkuxn4g'
MAPBOX_STYLE = 'mapbox://styles/redboot/cjnidreh14o5o2rs1vgnsol2p'

'''
FUNCTION:
    Outputs an image link based on the query
ARGS:
    str - the search query to search the image for
RETURNS:
    str - the photo source URL
'''
def get_image(query):
    spacelessQuery = query.replace(' ', '+')
    soup = bs4.BeautifulSoup(requests.get(f"https://google.com/search?q={spacelessQuery}&tbm=isch").text, 'lxml')
    for img in soup.select("img[alt]"):
        if query in img["alt"]:
             return img["src"]

ROCKETS = pd.read_excel('data/Rockets and spaceports.xlsx', 'Rockets')

PAST_LAUNCHES = scrap.getLaunches(past=True)
FUTURE_LAUNCHES = scrap.getLaunches()
LAUNCHES = pd.DataFrame(data=PAST_LAUNCHES + FUTURE_LAUNCHES)

# get rid of launches without a location
if not LAUNCHES.empty:
    LAUNCHES = LAUNCHES[~LAUNCHES['lat'].isna()]

    # get rid of repeating places
    density = LAUNCHES['lat'].value_counts()
    LAUNCHES['same'] = LAUNCHES['lat'].apply(lambda x: density[x])

if __name__ == '__main__':
    # for index, row in ROCKETS.iterrows():
    #     if pd.isnull(row["rocket"]):
    #         continue
    #     row["image"] = get_image("Rocket "+row["Rocket"])
    # ROCKETS.to_excel("data/Rockets and spaceports.xlsx")
    print(LAUNCHES.drop(['description', 'image', 'window'], axis=1))
