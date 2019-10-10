'''
Defines Main page and Rockets page layout.

Components:
    - launchComponent
    - mapComponent
    - rocketComponent
'''

import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import pandas as pd
import plotly.graph_objs as go

from consts import MAPBOX_ACCESS_TOKEN, MAPBOX_STYLE, ROCKETS, LAUNCHES, FUTURE_LAUNCHES

'''
ARGS:
    int - iteration index
    pd.Series - data to display
    bool - True if the card is a launch
    bool - True if the card is a rocket
RETURNS:
    html.Div - division to display
'''
def cardComponent(idx, data, launch=False, rocket=False):
    descriptors = []
    if launch:
        header = 'mission'
        descriptors = ['time', 'location', 'vehicle',
                      'pad', 'window', 'description']
    elif rocket:
        header = 'rocket'
        descriptors = ['company', 'country', 'site']

    return html.Div(
        className="card",
        children=[
            html.Div(
                className="card-header",
                children=[html.H1(f"{header.capitalize()} #{idx}: {data[header]}")],
            ),
            html.Div(
                className="card-main",
                children=[
                    html.Div(
                        className="card-image",
                        children=[
                            html.Img(src=data['image'])
                        ]
                    ),
                    html.Div(
                        className="card-description",
                        children=[
                            html.P(
                                children=[
                                    html.B(col.capitalize()), ': ' + str(data[col])
                                ]
                            ) 
                            for col in descriptors if str(data[col]) != "nan"
                        ]
                    )
                ]
            )
        ]
    )

def mapComponent(df):
    uniquePlaces = df.drop_duplicates(subset=['lat', 'long'], keep='first')
    return go.Figure(
        data=[
            go.Scattermapbox(
                lat=uniquePlaces['lat'],
                lon=uniquePlaces['long'],
                mode='markers',
                opacity=0.7,
                marker=dict(
                    sizemin=10,
                    size=uniquePlaces['same']*5,
                    color='limegreen'
                ),
                hoverinfo='text',
                hoverlabel={"font": {"size": 25,
                                     "family":"Lucida Console",
                                     "color":"black"}
                            },
                text=uniquePlaces['location'],
        )],
        layout=go.Layout(
            hovermode='closest',
            paper_bgcolor="rgb(0, 31, 31)",
            margin=go.layout.Margin(
                l=10,
                r=10,
                b=0,
                t=0,
                pad=8
            ),
            mapbox=dict(
                accesstoken=MAPBOX_ACCESS_TOKEN,
                style=MAPBOX_STYLE,
                bearing=0,
                center=dict(
                    lat=45,
                    lon=-73
                ),
                pitch=0,
                zoom=2
            )
        )
    )

ROCKETS_PAGE = [html.Div(
    html.H2("Rockets list", id="page-title")
)]+[cardComponent(index, data, rocket=True) for index, data in ROCKETS.iterrows()]

MAIN_PAGE = [
    dcc.Link('Rockets', id='rockets', className='link', href='/rockets'),
    html.A(href="https://clever-boyd-6ef0a3.netlify.com/",
           className='link',
           children="Info"),
    html.H1(id='page-title', children='LAUNCH.IO'),
    html.Div(id='Timer',children='0'),
    html.Div(id='next_launch'),
    html.Div(
        dcc.DatePickerRange(
            id='date_picker',
            min_date_allowed=dt(2000, 1, 1),
            max_date_allowed=dt(3000, 12, 31),
            initial_visible_month=dt.now(),
            start_date=dt.now(),
            end_date=dt.now() + datetime.timedelta(days=365)
        ),
        id='date_range'
    ),
    html.Div([
        dcc.Graph(
            id='map',
            figure=mapComponent(LAUNCHES),
            config={'displayModeBar': False}
        )
    ]),
    html.Div(
        dcc.Interval(
            id='interval-component',
            interval=1000,
            n_intervals=0
        )
    ),
    html.Div([
        dcc.Tabs(id="tabs", className="tabs", value='tab-2', children=[
            dcc.Tab(label='Selected location', value='tab-1', className='tab', selected_className="tab-selected"),
            dcc.Tab(label='All launches', value='tab-2', className='tab', selected_className="tab-selected"),
        ]),
        html.Div(
            id='rocket',
            children=[
                cardComponent(index+1, row, launch=True) for index, row in LAUNCHES.iterrows()
            ]
        )
    ])
]

if __name__ == '__main__':
    print()
