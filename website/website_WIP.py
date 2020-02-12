import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

# Neo4j Setup
from py2neo import Graph
import json

# Import class to make queries to Neo4j
from querier import Querier

# Dash Setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Connect to Neo4j
querier = Querier()

# This function returns all components for refresh
def serve_layout():
    return html.Div(children=[dark_theme()], style={'padding': '0px'})

# Set the website refresh to call a function
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
    html.H1(children='Gamer Matchmaking',style={'textAlign':'center'}),

    # Display total number of nodes in Neo4j graph
    daq.LEDDisplay(
        id='my-LED-display',
        color=theme['primary'],
        label={'label':"Total Player Nodes",'style':{'color':theme['primary']}},
        value=querier.num_nodes()
    ),

    # Display total number of relationships in Neo4j graph
    daq.LEDDisplay(
        id='my-LED-display2',
        color=theme['primary'],
        label={'label':"Total Relationships",\
                'style':{'color':theme['primary']}},
        value=querier.num_relationships()
    ),html.Br(),

    html.Button('Refresh',id='button',\
            style={'color':theme['primary'],'textAlign':'center'}),html.Br(),

    # Display dropdown to select Account IDs
    html.Label("Select an account and hero to create a team",\
            style={"font-size":"22px"}),
    dcc.Dropdown(
        id='account-selection',
        options=[
            {'label': 'Account ID A: 249840485', 'value': '249840485'},
            {'label': 'Account ID B: 205789808', 'value': '205789808'},
            {'label': 'Account ID C: 32096373', 'value': '32096373'},
            {'label': 'Account ID D: 80410028', 'value': '80410028'},
        ],
        value= '249840485'
    ),
    # Display results based on dropdown selection
    html.Label(id="top-heroes",style={"font-size":"22px"}),
    dcc.Slider(id='hero-slider',min=0,max=129,step=1,value=23),
    daq.LEDDisplay(
        id='selected-hero',
        color=theme['primary'],
        label={'label':"Selected Hero",\
                'style':{'color':theme['primary']}},
        value=0
    ),html.Br(),
    html.Label(id="team",style={"font-size":"22px"}),
    html.Div(html.P([html.Br()])),
    html.Label(id="teammates",style={"font-size":"22px"}),
    html.Div(html.P([html.Br()])),
    html.Label("This graph shows player interactions like killed, \
            healed, damaged.",
            style={"font-size":"18px"}),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    ),
    html.Div(html.P([html.Br()])),
    html.Label("This graph shows your popular heroes.",
            style={"font-size":"18px"}),
    dcc.Graph(
        id='hero-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    ),
    html.Div(html.P([html.Br()])),
    html.Label(id="wins",style={"font-size":"18px"}),
    html.Div(html.P([html.Br()])),
    html.Label(id="losses",style={"font-size":"18px"}),
    html.Div(html.P([html.Br()])),
    html.Label(id="killed-info",style={"font-size":"18px"}),
    html.Div(html.P([html.Br()])),
    html.Label(id="healed-info",style={"font-size":"18px"}),
    html.Div(html.P([html.Br()])),
    html.Label(id="damaged-info",style={"font-size":"18px"}),
    html.Div(html.P([html.Br()]))
])

# Returns components in dark theme
def dark_theme():
    return html.Div(children=[daq.DarkThemeProvider(\
            theme=theme,children=rootLayout)], 
            style={'backgroundColor':'#303030','color':theme['primary'],\
                    'border': 'solid 1px #A2B1C6', 'border-radius': '5px',\
                    'padding': '50px', 'margin-top': '20px'})


# Callback for dropdown to start neo4j query
@app.callback(
        dash.dependencies.Output('top-heroes', 'children'),
        [dash.dependencies.Input('account-selection', 'value')])
def update_output(value):
    output = "Your top heroes are: "
    result_json = querier.top_heroes(account_id=value)
    output += querier.json_to_string_heroes("which you played", result_json)
    return output

# LED button refresh
@app.callback(
    dash.dependencies.Output('my-LED-display', 'value'),
    [dash.dependencies.Input('button','n_clicks')]
)
def update_output(n_clicks):
    return querier.num_nodes()

# LED button refresh
@app.callback(
    dash.dependencies.Output('my-LED-display2', 'value'),
    [dash.dependencies.Input('button','n_clicks')]
)
def update_output(n_clicks):
    return querier.num_relationships()

# Slider to LED to display hero_id selected
@app.callback(
    dash.dependencies.Output('selected-hero', 'value'),
    [dash.dependencies.Input('hero-slider','value')]
)
def update_output(hero_id):
    return hero_id

# Query for teammate heroes with wins
@app.callback(
    dash.dependencies.Output('wins', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "You won the most with teammates playing the heroes: "
    results_json = querier.won_heroes(account_id=account_id, hero_id=hero_id)
    output += querier.json_to_string_heroes("was won with", result_json)
    return output

# Query for teammate heroes with losses
@app.callback(
    dash.dependencies.Output('losses', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "You lost the most with teammates playing the heroes: "
    results_json = querier.lost_heroes(account_id=account_id, hero_id=hero_id)
    output += querier.json_to_string_heroes("was lost with", result_json)
    return output

# Query for killed heroes
@app.callback(
    dash.dependencies.Output('killed-info', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    # Query for killed heroes
    output = "Your eliminated heroes are: "
    results_json = querier.killed_heroes(account_id=account_id, hero_id=hero_id)
    output += querier.json_to_string_heroes("elim.", result_json)
    return output

# Query for healed heroes
@app.callback(
    dash.dependencies.Output('healed-info', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "Your healed heroes are: "
    results_json = querier.healed_heroes(account_id=account_id, hero_id=hero_id)
    output += querier.json_to_string_heroes("healed", result_json)
    return output

# Query for damaged heroes
@app.callback(
    dash.dependencies.Output('damaged-info', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "Your damaged heroes are: "
    results_json = querier.healed_heroes(account_id=account_id, hero_id=hero_id)
    output += querier.json_to_string_heroes("damaged", result_json)
    return output

# Query for the balanced team
@app.callback(
    dash.dependencies.Output('team', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    try:
        heroes = {}
        # Query for getting win rate
        query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
                -[r:WON_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight ORDER BY r.weight DESC"
        top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
        for hero in top_heroes_json:
            hero_id2 = hero['h.hero_id']
            if hero_id != hero_id2:
                if hero_id2 not in heroes:
                    heroes[hero_id2] = 1
                else:
                    heroes[hero_id2] += 1

        # Query for getting loss rate
        query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
                -[r:LOST_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight ORDER BY r.weight DESC"
        top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
        for hero in top_heroes_json:
            hero_id2 = hero['h.hero_id']
            if hero_id != hero_id2:
                if hero_id2 not in heroes:
                    heroes[hero_id2] = 0
                else:
                    heroes[hero_id2] -= 1

        # Query for getting healed heroes
        query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+\
                "'})-[r:HEALED]->(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight ORDER BY r.weight DESC"
        top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
        for hero in top_heroes_json:
            hero_id2 = hero['h.hero_id']
            if hero_id != hero_id2:
                if hero_id2 not in heroes:
                    heroes[hero_id2] = 2
                else:
                    heroes[hero_id2] += 2

        output = "Factoring in wins, losses, and heals, \
                your team should have the heroes: "
        if heroes == {}:
            return "Check hero_id selection with slider to match top heroes"
        output += str(sorted(heroes, key=heroes.get, reverse=True)[:4])
        return output
    except e as Exception:
        return repr(e)

# Query for the balanced team
@app.callback(
    dash.dependencies.Output('teammates', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "You work best with players: "
    results_json = querier.win_players(account_id=account_id, hero_id=hero_id)
    output += querier.json_to_string_players(result_json)
    return output
    
# Graph hero stats
@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    # Query for killed heroes
    k_heroes = []
    k_weights = []
    top_heroes_json = querier.killed_heroes(account_id=account_id, hero_id=hero_id)
    for hero in top_heroes_json:
        k_heroes.append(hero['h.hero_id'])
        k_weights.append(hero['r.weight'])

    # Query for getting healed heroes
    h_heroes = []
    h_weights = []
    top_heroes_json = querier.healed_heroes(account_id=account_id, hero_id=hero_id)
    for hero in top_heroes_json:
        h_heroes.append(hero['h.hero_id'])
        h_weights.append(hero['r.weight'])

    # Query for getting damaged heroes
    d_heroes = []
    d_weights = []
    top_heroes_json = querier.damaged_heroes(account_id=account_id, hero_id=hero_id)
    for hero in top_heroes_json:
        d_heroes.append(hero['h.hero_id'])
        d_weights.append(hero['r.weight'])
    figure={
        'data': [
            {'x':k_heroes, 'y': k_weights, 'type': 'bar', 'name':'eliminated'},
            {'x':h_heroes, 'y': h_weights, 'type': 'bar', 'name':'healed'},
            {'x':d_heroes, 'y': d_weights, 'type': 'bar', 'name':'damaged'},
        ],
        'layout':{'title': 'Your Interactions with Other Heroes'}
    }
    return figure

@app.callback(
    dash.dependencies.Output('hero-graph', 'figure'),
    [dash.dependencies.Input('account-selection','value')]
)
def update_output(account_id):
    heroes = []
    weights = []
    top_heroes_json = querier.top_heroes(account_id=account_id, hero_id=hero_id)
    for hero in top_heroes_json:
        heroes.append(hero['h.hero_id'])
        weights.append(hero['r.weight'])

    figure={
        'data': [
            {'x': heroes, 'y': weights,'type': 'bar', 'name':'hero-stats'},
        ],
        'layout':{'title': 'Your Heroes'}
    }
    return figure

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True)
