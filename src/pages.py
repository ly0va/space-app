import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from datetime import datetime as dt
import plotly.graph_objs as go
import pandas as pd
from consts import MAPBOX_ACCESS_TOKEN, MAPBOX_STYLE, ROCKETS, LAUNCHES

def divTemplate(idx, row):
    return html.Div(
        className="launch",
        children=[
            html.Div(
                className="top",
                children=[html.H1(f"Mission #{idx}" + ": "+row['mission'])],
            ),
            html.Div(
                className="bottom",
                children=[
                    html.Img(src=row['image']),
                    html.Div(className="text",
                    children=[
                        html.Div(
                            className="info",
                            children=[
                                html.P(children=[html.B(children=k.capitalize()), ': '+ str(v)])
                                for k, v in row.items()
                                if k in ['vehicle', 'time', 'location', 'pad', 'window'] and str(v) != "nan"
                            ]
                        ),
                        html.Div(
                            className="description",
                            children=row['description'],
                        )
                    ])

                ]
            )
        ]
    )

def mapTemplate(df):
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

def render_rocket(idx, row):
    if pd.isnull(row.values).any():
        return ''
    return html.Div(
        className="rocketinfo",
        children=[
            html.Div(
                className="top",
                children=[html.H1(f"Rocket #{int(idx+1)}" + ": "+row['Rocket'])],
            ),
            html.Div(
                className="bottom",
                children=[
                    html.Img(src=row["Photo"]),
                    html.Div(
                        className="text",
                        children=[
                            html.P(children=[html.B(children=k), ': '+ str(v)])
                            for k, v in row.items()
                            if k in ['Company', 'Country'] and str(v).lower() != "nan"
                        ]+[html.P(children=[html.B("Site"), ': ', html.A(row["Site"], href=row["Site"])])]
                    )
                ]
            )
        ]
    )

ROCKETS_PAGE = [html.Div(
    html.H1("Rockets list", className="title")
)]+[render_rocket(index, row) for index, row in ROCKETS.iterrows()]

INDEX_PAGE = [
    dcc.Link('Home', href='/home'),
    html.Br(),
    dcc.Link('Rockets', href='/rockets')
]

MAIN_PAGE = [
    dcc.Link('Rockets', id='rockets', className='ref', href='/rockets'),
    html.A(href="https://clever-boyd-6ef0a3.netlify.com/",
           className='ref',
           children="Info"),
    html.H1(id='name', children='LAUNCH.IO'),
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
            figure=mapTemplate(LAUNCHES),
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
            dcc.Tab(label='This location', value='tab-1', className='tab', selected_className="tab-selected"),
            dcc.Tab(label='ALL', value='tab-2', className='tab', selected_className="tab-selected"),
        ]),
        html.Div(
            id='rocket',
            children=[divTemplate(index, row) for index, row in LAUNCHES.iterrows()]
        )
    ])
]

if __name__ == '__main__':
    print()
