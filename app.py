from datetime import datetime as dt
from consts import DATE_FORMAT

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

from pages import cardComponent, mapComponent, MAIN_PAGE, ROCKETS_PAGE, LAUNCHES, FUTURE_LAUNCHES

TBD = dt(3000, 12, 31)

app = dash.Dash(__name__)
server = app.server

app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(className='main', id='Main')
    ]
)

'''
FUNCTION:
    Converts date string to datetime. 
ARGS:
    str - time to parse
RETURNS:
    datetime - converted time
'''
def toTimeDate(timeString):
    # If the time is not defined return a point in future.
    if timeString == 'TBD':
        return TBD
    else:
        return dt.strptime(timeString[-20:-1], DATE_FORMAT)


'''
FUNCTION:
    Checks if the launch time is valid to display.
    Returns True if time is between start and finish or yet TBD
ARGS:
    str - starting time
    str - finishing time
    datetime - time to check
RETURNS:
    bool - verdict
'''
def validLaunchTime(start, finish, time):
    return dt.strptime(start[:10], '%Y-%m-%d') <= time and \
           time <= dt.strptime(finish[:10], '%Y-%m-%d') or \
           time == TBD

#################################################
################## CALLBACKS ####################
#################################################

'''Routing'''
@app.callback(Output('Main', 'children'),
              [Input('url', 'pathname')])
def displayRocketList(path_name):
    if path_name == '/':
        return MAIN_PAGE
    elif path_name == '/rockets':
        return ROCKETS_PAGE
    else:
        return [
            dcc.Link('Home', href='/home'),
            html.Br(),
            dcc.Link('Rockets', href='/rockets')
        ]

'''Update markers on Date Picker update'''
@app.callback(Output('map', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')])
def updateMarkersOnDate(st, fin):
    if st and fin:
        times = LAUNCHES['time'].apply(toTimeDate)
        times = times.apply(lambda x: validLaunchTime(st, fin, x))
        return mapComponent(LAUNCHES[times])
    else:
        return mapComponent(LAUNCHES)

'''Update Rocket list on Date Picker update / Tab change / Map Click'''
@app.callback(Output('rocket', 'children'),
              [Input('map', 'clickData'),
               Input('tabs', 'value'),
               Input('date_picker', 'start_date'),
               Input('date_picker', 'end_date')])
def updateLaunchList(clickData, tab, st, fin):
    if tab == 'tab-1':
        # show launches in a specific location
        if not clickData:
            return html.Div(style={'height': "1000px"})
        # select the launches with the same coords as the place selected
        sameCoords = LAUNCHES['lat'] == clickData['points'][0]['lat']
        validTimes = LAUNCHES['time'].apply(toTimeDate)
        validTimes = validTimes.apply(lambda x: validLaunchTime(st, fin, x))
        launch = LAUNCHES[sameCoords & validTimes]
        return [cardComponent(index+1, row, launch=True) for index, row in launch.iterrows()]
    elif tab == 'tab-2':
        # show all the launches
        return [cardComponent(index+1, row, launch=True) for index, row in LAUNCHES.iterrows()]

'''Update timer with time until next launch'''
@app.callback(Output('Timer', 'children'),
              [Input('interval-component', 'n_intervals')])
def timeToNearestLaunch(n):
    T = FUTURE_LAUNCHES[0]['time']
    if T == 'TBD':
        timeDisplayed = 'TBD'
    else:
        T = T[-20:-1]

        diff = dt.strptime(T, DATE_FORMAT) - dt.utcnow()
        hours, minutes = divmod(diff.seconds/60,60)
        timeDisplayed = ' {} days {} hours {} minutes {} seconds'.format(diff.days,
                                                                         int(hours),
                                                                         int(minutes),
                                                                         diff.seconds % 60)
    return [html.H1([
                html.A('Next launch:', className='link', id='show-next-launch'),
                html.H1(timeDisplayed, id='timer')
            ])]

showing_next_launch_info = False

'''Trigger showing next launch information'''
@app.callback(Output('next-launch-description', 'children'),
              [Input('show-next-launch', 'n_clicks')])
def showNextLaunchInfo(n_clicks):
    if n_clicks:
        global showing_next_launch_info
        if showing_next_launch_info:
            showing_next_launch_info = False
            return ''
        else:
            showing_next_launch_info = True
            return cardComponent(1, FUTURE_LAUNCHES[0], launch=True)

if __name__ == '__main__':
    #app.scripts.config.serve_locally = False
    app.run_server()
