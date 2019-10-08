from datetime import datetime as dt

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

from pages import divTemplate, mapTemplate, INDEX_PAGE, MAIN_PAGE, ROCKETS_PAGE, LAUNCHES, FUTURE_LAUNCHES

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
        return dt(3000, 12, 31)
    else:
        return dt.strptime(timeString[-20:-1], '%Y-%m-%d %H:%M:%S')

#################################################
################## CALL BACKS ###################
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
        return INDEX_PAGE

'''On Date Picker update'''
@app.callback(Output('map', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')])
def updateMarkersOnDate(st, fin):
    if st and fin:
        times = LAUNCHES['time'].apply(toTimeDate)
        times = times.apply(lambda x: dt.strptime(st[:10], '%Y-%m-%d') <= \
                                      x <= \
                                      dt.strptime(fin[:10], '%Y-%m-%d'))
        return mapTemplate(LAUNCHES[times])
    else:
        return mapTemplate(LAUNCHES)

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
        comp = lambda x : dt.strptime(st[:10], '%Y-%m-%d') <= \
                          toTimeDate(x) <= \
                          dt.strptime(fin[:10], '%Y-%m-%d')
        inDateRange = LAUNCHES['time'].apply(comp)
        launch = LAUNCHES[sameCoords & inDateRange]
        return [divTemplate(index, row) for index, row in launch.iterrows()]
    elif tab == 'tab-2':
        # show all the launches
        return [divTemplate(index, row) for index, row in LAUNCHES.iterrows()]

'''Update timer'''
@app.callback(Output('Timer', 'children'),
              [Input('interval-component', 'n_intervals')])
def timeToNearestLaunch(n):
    T = FUTURE_LAUNCHES[0]['time']
    T = T[-20:-1]

    diff = dt.strptime(T, '%Y-%m-%d %H:%M:%S') - dt.utcnow()
    hours, minutes = divmod(diff.seconds/60,60)
    return [html.H1([
                html.A('Next launch:', className='ref', id='next_launch_link'),
                html.H1(
                    ' {} days {} hours {} minutes {} seconds'.format(diff.days,
                                                                     int(hours),
                                                                     int(minutes),
                                                                     diff.seconds%60),
                    id='timer'
                )
            ])]

showing_next_launch_info = False

'''Trigger showing next launch information'''
@app.callback(Output('next_launch', 'children'),
              [Input('next_launch_link', 'n_clicks')])
def showNextLaunchInfo(n_clicks):
    if n_clicks:
        global showing_next_launch_info
        if (showing_next_launch_info):
            showing_next_launch_info = False
            return ''
        else:
            showing_next_launch_info = True
            return divTemplate(1, FUTURE_LAUNCHES[0])

if __name__ == '__main__':
    #app.scripts.config.serve_locally = False
    app.run_server(debug=True)
