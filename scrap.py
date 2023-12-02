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

def getLaunches(past=False):
    '''Returns a dict containing info about launches 
    
    Args:
        past (bool): - determines which launches to show (past or future)
    
    Returns:
        [{'image': str, 'mission': str, 'description': str, 'vehicle': str,
        'time': str, 'location':str, 'pad': str, 'lat': float, 'long': float}] - list of all launches
    '''

    launchesUrl = "https://ll.thespacedevs.com/2.2.0/launch"
    
    if past:
        launchesUrl += "/previous"
    else:
        launchesUrl += "/upcoming"
    
    print(f"Getting launches from {launchesUrl}")
    response = requests.get(launchesUrl)
    if response.status_code != 200:
        print(f"Error {response.status_code} {response.json()}")
        return []
    print(response.json())
    launches: list = response.json()['results'] 
    return list(map(mapLaunchResponse, launches))

def mapLaunchResponse(launchResponse):
    return {
        'image': launchResponse['image'],
        'mission': launchResponse['mission']['name'],
        'description': launchResponse['mission']['description'],
        'vehicle': launchResponse['rocket']['configuration']['name'],
        'time': launchResponse['window_start'],
        'location': launchResponse['pad']['location']['name'],
        'pad': launchResponse['pad']['name'],
        'lat': launchResponse['pad']['latitude'],
        'long': launchResponse['pad']['longitude']
    }

if __name__ == '__main__':
    from pprint import pprint
    # print('Please enter your Google API key:')
    # key = input()
    # updatePlaces(key)
    launches = getLaunches()
    for l in launches:
        # pprint(l['mission'])
        # pprint(l['location'])
        # pprint(l['lat'])
        pprint(l)
        print()
