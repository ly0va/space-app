import json

import requests
from bs4 import BeautifulSoup

'''
FUNCTION:
    Converts address string to lat-long coordinates
ARGS:
    str - address to search for
    key - Google API key
RETURNS:
    {'lat': float, 'lng': float} - coordinates
'''
def geocode(address, key):
    address = address.replace(' ', '+')
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={key}&address={address}"
    response = requests.get(url).json()
    if not response['results']:
        raise Exception("geocode: The address specified does not exist.")

    coordinates = response['results'][0]['geometry']['location']
    for k, v in coordinates.items():
        coordinates[k] = round(v, 7)
    return coordinates

'''
FUNCTION:
    Saves the launch places (address and coords) in a json
ARGS:
    str - Google API Key
RETURNS:
    {str: {'lat': float, 'lng': float}} - set of places and respective coordinates
'''
def updatePlaces(key):
    LINK = "http://www.spaceflightinsider.com/launch-schedule/"

    with open('data/places.txt') as fin:
        places = json.load(fin)
    
    for url in [LINK, LINK+"?past=1"]:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')

        for tag in soup.select("table.launchcalendar"):
            # get the description of every rocket
            result = {}
            details = tag.find(class_="launchdetails").find_all("tr")

            for detail in details:
                result[detail.th.string.lower()] = detail.td.get_text()

            place = result['location'].split(' ')
            # get rid of the code at the end
            result['location'] = ' '.join(place[:-1])
            coordinates = places.get(result['location'], geocode(result['location'], key))
            places[result['location']] = coordinates

    with open('data/places.txt', 'w') as fout:
        json.dump(places, fout)

    return places

'''
FUNCTION:
    Returns a dict containing info about future launches 
ARGS:
    bool - determines which launches to show (past or future)
RETURNS:
    [{'image': str, 'mission': str, 'description': str, 
      'location':str, 'pad': str, 'lat': float, 'long': float}] - list of all launches
'''
def getLaunches(past=False):
    LINK = "http://www.spaceflightinsider.com/launch-schedule/"
    if past:
        LINK += "?past=1"
    page = requests.get(LINK)
    soup = BeautifulSoup(page.text, 'lxml')

    # open all saved places and their coords
    with open('data/places.txt') as fin:
        places = json.load(fin)

    launches = []
    for tag in soup.select("table.launchcalendar"):
        result = {}
        details = tag.find(class_="launchdetails").find_all("tr")

        for detail in details:
            result[detail.th.string.lower()] = detail.td.get_text()

        style = tag.find(class_='vehicle').div['style']
        index = style.index("http")
        result['image'] = style[index:-3]
        result['mission'] = tag.find(colspan='2').get_text()
        result['description'] = tag.find(class_='description').p.get_text()
        place = result['location'].split(' ')
        result['location'] = ' '.join(place[:-1])
        result['pad'] = place[-1]
        coordinates = places.get(result['location'], None)
        if coordinates:
            result['long'] = coordinates.get('lng', None)
            result['lat'] = coordinates.get('lat', None)
        launches.append(result)

    return launches

if __name__ == '__main__':
    from pprint import pprint
    # print('Please enter your Google API key:')
    # key = input()
    # updatePlaces(key)
    launches = getLaunches()
    for l in launches:
        pprint(l['mission'])
        pprint(l['location'])
        pprint(l['lat'])
        print()
