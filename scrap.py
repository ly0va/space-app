import requests
from bs4 import BeautifulSoup
 
key = "AIzaSyAUkNMzDo7KUo2TrCYYF9ENig32N7RJYg4"

def getLaunches(past=False):
    ''' Returns a dict containing info about future launches '''

    url = "http://www.spaceflightinsider.com/launch-schedule/"
    if past:
        url += "?past=1"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    launches = []
    places = {}

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
        coordinates = places.get(result['location'], geocode(result['location']))
        places[result['location']] = coordinates
        result['long'] = coordinates.get('lng', None)
        result['lat'] = coordinates.get('lat', None)
        launches.append(result)

    return launches


def geocode(address):
    ''' converts address string to lat-long coordinates '''
    address = address.replace(' ', '+')
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={key}&address={address}"
    response = requests.get(url).json()
    if not response['results']:
        return {}
    coordinates = response['results'][0]['geometry']['location']
    for k, v in coordinates.items():
        coordinates[k] = round(v, 7)
    return coordinates


if __name__ == '__main__':
    from pprint import pprint
    launches = getLaunches(True)
    launches.sort(key=lambda l: l['location'])
    for launch in launches:
        print(launch['lat'], launch['long'])
        pprint(launch['location'])
        pprint(launch['pad'])
        print()
