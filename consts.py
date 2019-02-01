import pandas as pd
import scrap
import requests
import bs4

MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYW5kcmV5ZGVuIiwiYSI6ImNqbmhwdGlkMjBhYzQzanJzbTM3NzdobW8ifQ.ZR_vrBuTDB1-byVDkuxn4g'
MAPBOX_STYLE = 'mapbox://styles/redboot/cjnidreh14o5o2rs1vgnsol2p'

def get_image(query):
    '''Outputs an image link based on the query (text)'''
    pquery = query.replace(' ', '+')
    soup = bs4.BeautifulSoup(requests.get(f"https://google.com/search?q={pquery}&tbm=isch").text, 'lxml')
    for img in soup.select("img[alt]"):
        if query in img["alt"]:
             return img["src"]

ROCKETS = pd.read_excel('Rockets and spaceports.xlsx', 'Rockets')
# add photos
for index, row in ROCKETS.iterrows():
    if pd.isnull(row["Rocket"]): continue
    row["Photo"] = get_image("Rocket "+row["Rocket"])

PAST_LAUNCHES = scrap.getLaunches(True)
FUTURE_LAUNCHES = scrap.getLaunches()
LAUNCHES = pd.DataFrame(data=PAST_LAUNCHES+FUTURE_LAUNCHES)
# get rid of launches without a location
LAUNCHES = LAUNCHES[~LAUNCHES['lat'].isna()]
# get rid of repeating places
density = LAUNCHES['lat'].value_counts()
LAUNCHES['same'] = LAUNCHES['lat'].apply(lambda x: density[x])

if __name__ == '__main__':
    from pprint import pprint
    print(LAUNCHES)
