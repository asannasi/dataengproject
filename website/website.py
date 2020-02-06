import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

# Neo4j Setup
from py2neo import Graph
graph = Graph("bolt://10.0.0.12:7687")

# Dash Setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# This function returns all components for refresh
def serve_layout():
    return html.Div(children=[dark_theme()], style={'padding': '0px'})
app.layout = serve_layout

# Colors for dark theme
theme = {
    'dark': True,
    'detail': '#149414',
    'primary': '#00EA64', 
    'secondary': '#6E6E6E'
}

# This layout is for components in the dark theme
rootLayout = html.Div(children=[
    # Title
    html.H1(children='Gamer Matchmaking: A Winning Team is a Good Team',style={'textAlign':'center'}),

    # Display total number of nodes in Neo4j graph
    daq.LEDDisplay(
        id='my-LED-display',
        color=theme['primary'],
        label={'label':"Total Player Nodes",'style':{'color':theme['primary']}},
        value=len(graph.nodes)
    ),html.Br(),

    # Display total number of relationships in Neo4j graph
    daq.LEDDisplay(
        id='my-LED-display2',
        color=theme['primary'],
        label={'label':"Total Relationships",'style':{'color':theme['primary']}},
        value=len(graph.relationships)
    ),html.Br(),

    # Display dropdown to select Account IDs
    html.Label("Select an account to create a team"),
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'sunstreaker', 'value': '200002065'},
            {'label': 'shockwave', 'value': '107231795'},
            {'label': 'wheeljack', 'value': '139151127'}
        ],
        value='139151127'
    ),
    # Display results based on dropdown selection
    html.Label(id="dropdown-output"),

    # Display Team
    html.Label("..."),
    html.Label("The above is the table returned by a Cypher query. The format is account_id | win_rate."),
    html.Label("You can imagine taking the first 5 players as a team since they have the highest win rate together."),
])

# Returns components in dark theme
def dark_theme():
    return html.Div(children=[daq.DarkThemeProvider(theme=theme,children=rootLayout)], 
            style={'backgroundColor':'#303030','color':theme['primary'],'border': 'solid 1px #A2B1C6', 'border-radius': '5px', 'padding': '50px', 'margin-top': '20px'})

# Callback for dropdown to start neo4j query
@app.callback(
        dash.dependencies.Output('dropdown-output', 'children'),
        [dash.dependencies.Input('demo-dropdown', 'value')])
def update_output(value):
    query = "MATCH (a:Player{account_id:'" + str(value) +"'})-[:LOST_WITH|:WON_WITH]-(c)  WITH a,c,toFloat(size((a)-[:LOST_WITH]-(c))) AS losses,(toFloat(size((a)-[:WON_WITH]-(c)))) AS wins RETURN c.account_id,toFloat(wins/(losses+wins)) AS win_rate ORDER BY win_rate DESC;"
    q = graph.run(query)
    return repr(q.to_table())

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True)
