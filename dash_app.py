import dash
from dash import dash_table
from dash import dcc
from dash import html, Input, Output
import dash_leaflet as dl
import pandas as pd
import plotly.express as px

from os import environ
from AnimalShelter import AnimalShelter

# MongoDB connection details
username = "aacuser"
password = "aacPassword"
host = environ.get('MONGO_HOST')
port = int(environ.get('MONGO_PORT'))
db = 'AAC'
col = 'animals'

# Create an instance of AnimalShelter
shelter = AnimalShelter(username, password, host, port, db, col)
df = None

try:
    # Read data from the animal shelter
    animals = shelter.read({})
    df = pd.DataFrame.from_records(shelter.read({}))
except:
    print(shelter._lastException)

# Create the Dash application
app = dash.Dash()
app.layout = html.Div(
    children=[
        html.Div(
            className='header-container',
            style={'width': '100%', 'height': '100%'},
            children=[
                html.A(href='https://www.snhu.edu', children=[
                    html.Img(src='assets/site_logo.png', className='site-logo')
                ]),
                html.H2(
                    style={'display': 'inline-block'},
                    children=[
                        'Matching Rescue Operations with Shelter Dogs',
                        html.Br(),
                        'An app by Christopher Richards' 
                    ]
                )
            ]
        ),
        html.Label('Filter:'),
        dcc.RadioItems(
            id='filter_options',
            options=[
                'All',
                'Water',
                'Mountain or Wilderness',
                'Disaster or Individual Tracking'
            ],
            value='All',
            inline=True
        ),
        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            row_selectable='single',
            selected_rows=0,
            id='shelter_table',
            page_current=0,
            page_size=10
        ),
        html.Div(
            style={'display': 'inline-block'},
            children=dcc.Graph(
                id='graph',
                style={'width': '600px', 'height': '400px'}
            )
        ),
        html.Div(
            style={'display': 'inline-block', 'width': '600px', 'height': '400px'},
            id='map',
        )
    ]
)

# Callback function to update the map
@app.callback(Output('map', 'children'), [Input('shelter_table', 'derived_virtual_data'),
                                             Input('shelter_table', 'derived_virtual_selected_rows')])
def update_map(data, row_index):
    center = []
    if row_index == [] or row_index is None:
        row_index = 0
    else:
        row_index = row_index[0]
    if data is None:
        return None
    dff = pd.DataFrame.from_dict(data)
    print(data)
    center = [dff.iloc[row_index, 13], dff.iloc[row_index, 14]]
    
    return dl.Map(
        style={'width': '100%', 'height': '100%'},
        center=center, zoom=10, children=[
            dl.TileLayer(id='base-layer-id'),
            dl.Marker(position=center, children=[
                dl.Tooltip(dff.iloc[row_index, 9]),
                dl.Popup([
                    html.H2('Animal Name'),
                    html.H3(dff.iloc[row_index, 9])
                ])
            ])
        ]
    )

# Callback function to update the graph
@app.callback(Output('graph', 'figure'), [Input('filter_options', 'value')])
def update_chart(filter):
    ddf = return_filtered_query(filter)
    ddf = ddf.groupby('breed')['breed'].count().reset_index(name='count')
    return px.pie(ddf, names='breed', values='count', hole=0.3)

# Callback function to filter and update the data table
@app.callback(Output('shelter_table', 'data'), [Input('filter_options', 'value')])
def filter_results(value):
    return return_filtered_query(value).to_dict('records')
    
# Function to return a filtered query based on the selected filter
def return_filtered_query(filter):
    filter_map = {
        'Water': {
            'animal_type': 'Dog',
            'breed': ['Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland'],
            'sex': 'Intact Female',
            'age_low': 26,
            'age_high': 156
        },
        'Mountain or Wilderness': {
            'animal_type': 'Dog',
            'breed': ['German Shepard', 'Alaskan Malamute', 'Old English Sheepdog', 'Siberian Husky', 'Rottweiler'],
            'sex': 'Intact Male',
            'age_low': 26,
            'age_high': 156
        },
        'Disaster or Individual Tracking': {
            'animal_type': 'Dog',
            'breed': ['Doberman Pinscher', 'German Shepard', 'Golden Retriever', 'Bloodhound', 'Rottweiler'],
            'sex': 'Intact Male',
            'age_low': 20,
            'age_high': 300
        }
    }
    if filter == 'All':
        ddf = pd.DataFrame.from_records(shelter.read({}))
        print(ddf)
        return ddf
    filter_type = filter_map[filter]
    print(filter_type['breed'])
    query_filter = {
        'animal_type': filter_type['animal_type'],
        'sex_upon_outcome': filter_type['sex'],
        'age_upon_outcome_in_weeks' :{'$gte': filter_type['age_low'], '$lte': filter_type['age_high']},
        'breed': {'$in': filter_type['breed']}
    }
    ddf = pd.DataFrame.from_records(shelter.read(query_filter))
    print(ddf)
    return ddf

# Run the Dash application server
app.run_server()