import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import datetime
import numpy as np
import plotly.graph_objs as go
from riverrunner.repository import Repository
from riverrunner import settings


repo = Repository()
runs = repo.get_all_runs_as_list()
options = [r.select_option for r in runs]
del repo

app = dash.Dash()
font_url = 'https://fonts.googleapis.com/css?family=Montserrat|Permanent+Marker'
app.css.append_css({
    'external_url': font_url
})

app.layout = html.Div([
    html.Div(
        id='navbar',
        children=[
            html.H2('River Runners',
                    id='heading',
                    style={'fontFamily': 'Permanent Marker'}
                    )
        ],
        style={
            'width': '100%',
            'textAlign': 'center',
            'backgroundColor': '#7FA5ED'
        }),
    html.Div(
        id='river_selection_container',
        children=[
            dcc.Dropdown(
                id='river_dropdown',
                options=options,
                value=599,
                multi=False
            )
        ],
        style={
            'width': '80%',
            'padding': 10,
            'textAlign': 'center',
            'marginLeft': 'auto',
            'marginRight': 'auto'
        }
    ),
    html.Div(
        id='ts_container',
        children=dcc.Graph(id='time_series'),
    ),
    html.Div(id='map_container',
             children=dcc.Graph(
                 id='river_map',
                 figure={
                     'data': [{
                         'lat': list(map(lambda run: run.put_in_latitude, runs)),
                         'lon': list(map(lambda run: run.put_in_longitude, runs)),
                         'type': 'scattermapbox'
                     }],
                     'layout': {
                         'autosize': True,
                         'hovermode': 'closest',
                         'mapbox': {
                             'accesstoken': settings.MAPBOX,
                             'center': {
                                 'lat': 47,
                                 'lon': -119
                             },
                             'zoom': 6
                         },
                         'margin': {
                             'l': 10, 'r': 10, 'b': 0, 't': 0
                         }
                     }
                 }
             ),
             style={
                 'minHeight': 400
             }
         )
    ],
    style={
        'font-family': ['Montserrat', 'sans-serif']
    }
)


@app.callback(Output('time_series', 'figure'), [
                  Input('river_dropdown', 'value'),
                  Input('heading', 'children')
                ]
              )
def update_timeseries(value=599, pl=None):
    if not isinstance(value, int):
        return None

    repo = Repository()
    predictions = repo.get_predictions(value)
    if predictions is None:
        return None

    observed = go.Scatter(
        x=predictions['observed']['dates'],
        y=predictions['observed']['values'],
        line=dict(
            color='#252E75',
            width=4
        )
    )

    predicted = go.Scatter(
        x=predictions['predicted']['dates'],
        y=predictions['predicted']['values'],
        line=dict(
            color='#C44200',
            width=4
        )
    )

    max_line = go.Scatter(
        x=[np.min(predictions['dates']), np.max([predictions['dates']])],
        y=[predictions['max_fr'], predictions['max_fr']],
        line=dict(
            color='#123B38',
            width=1,
            dash='dot')
    )

    min_line = go.Scatter(
        x=[np.min(predictions['dates']), np.max([predictions['dates']])],
        y=[predictions['min_fr'], predictions['min_fr']],
        line=dict(
            color='#123B38',
            width=1,
            dash='dot')
    )

    layout = go.Layout(title="Flow Rate", xaxis={'title': 'Date'}, yaxis={'title': 'Flow Rate'},
                       shapes=[{
                                'type': 'rect',
                                'xref': 'x',
                                'yref': 'y',
                                'x0': np.min(predictions['dates']),
                                'y0': predictions['min_fr'],
                                'x1': np.max(predictions['dates']),
                                'y1': predictions['max_fr'],
                                'fillcolor': '#d3d3d3',
                                'opacity': 0.2,
                                'line': {
                                    'width': 0,
                                }
                            }
                       ])

    fig = go.Figure(data=[observed, predicted, max_line, min_line], layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')
