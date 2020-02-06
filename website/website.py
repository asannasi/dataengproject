import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

theme = {
            'dark': True,
                'detail': '#007439',
                    'primary': '#00EA64', 
                        'secondary': '#6E6E6E'
                        }
rootLayout = html.Div(children=[
        daq.LEDDisplay(
                    id='my-LED-display',
                    color=theme['primary'],
                            label="Default",
                                    value=6
                                        ),html.Br()
    ])

app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),
        
            daq.BooleanSwitch(
                id='my-daq-booleanswitch',
                on=True
            ),  
            html.Div(children=[daq.DarkThemeProvider(theme=theme,children=rootLayout)
                ], style={'backgroundColor':'#303030','border': 'solid 1px #A2B1C6', 'border-radius': '5px', 'padding': '50px', 'margin-top': '20px'})
], style={'padding': '50px'})


if __name__ == '__main__':
        app.run_server(host='0.0.0.0',debug=True)
