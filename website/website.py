import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

# Neo4j Setup
from py2neo import Graph
import json

# Dash Setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# This function returns all components for refresh
graph = Graph("bolt://10.0.0.12:7687")
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
    html.H1(children='Gamer Matchmaking',style={'textAlign':'center'}),

    # Display total number of nodes in Neo4j graph
    daq.LEDDisplay(
        id='my-LED-display',
        color=theme['primary'],
        label={'label':"Total Player Nodes",'style':{'color':theme['primary']}},
        value=str(len(graph.nodes))
    ),

    # Display total number of relationships in Neo4j graph
    daq.LEDDisplay(
        id='my-LED-display2',
        color=theme['primary'],
        label={'label':"Total Relationships",\
                'style':{'color':theme['primary']}},
        value=str(len(graph.relationships))
    ),html.Br(),

    html.Button('Refresh',id='button',\
            style={'color':theme['primary'],'textAlign':'center'}),html.Br(),

    # Display dropdown to select Account IDs
    html.Label("Select an account and hero to create a team",style={"font-size":"22px"}),
    dcc.Dropdown(
        id='account-selection',
        options=[
            {'label': 'Account ID A: 249840485', 'value': '249840485'},
            {'label': 'Account ID B: 205789808', 'value': '205789808'},
            {'label': 'Account ID C: 122256595', 'value': '122256595'},
            {'label': 'Account ID D: 200002065', 'value': '200002065'},
            {'label': 'Account ID E: 80410028', 'value': '80410028'},
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
    html.Label(id="team",style={"font-size":"36px"}),
    html.Div(html.P([html.Br()])),
    html.Label(id="wins-losses",style={"font-size":"22px"}),
    html.Label(id="killed-info",style={"font-size":"22px"})
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
    query = "MATCH (p:Player{account_id:'"+str(value)+"'})\
            -[r:PLAYED_AS]->(a:Avatar)-[:IS]-(h:Hero)\
            RETURN h.hero_id, r.weight ORDER BY r.weight DESC LIMIT 5"
    top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
    for hero in top_heroes_json:
        output += "Hero " + str(hero['h.hero_id']) + " which you played " +\
                 str(hero['r.weight']) + " times, "
    return output

@app.callback(
    dash.dependencies.Output('my-LED-display', 'value'),
    [dash.dependencies.Input('button','n_clicks')]
)
def update_output(n_clicks):
    graph = Graph("bolt://10.0.0.12:7687")
    return str(len(graph.nodes))

@app.callback(
    dash.dependencies.Output('my-LED-display2', 'value'),
    [dash.dependencies.Input('button','n_clicks')]
)
def update_output(n_clicks):
    graph = Graph("bolt://10.0.0.12:7687")
    return str(len(graph.relationships))

@app.callback(
    dash.dependencies.Output('selected-hero', 'value'),
    [dash.dependencies.Input('hero-slider','value')]
)
def update_output(hero_id):
    return hero_id

@app.callback(
    dash.dependencies.Output('wins-losses', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "You won the most with teammates playing the heroes: "
    query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
            -[r:WON_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
            RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
    top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
    for hero in top_heroes_json:
        output += "Hero " + str(hero['h.hero_id']) + " was won with " +\
                 str(hero['r.weight']) + " times, "

    output += "You lost the most with teammates playing the heroes: "
    query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
            -[r:LOST_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
            RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
    top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
    for hero in top_heroes_json:
        output += "Hero " + str(hero['h.hero_id']) + " was lost with " +\
                 str(hero['r.weight']) + " times, "
    return output

@app.callback(
    dash.dependencies.Output('killed-info', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    output = "Your killed heroes are: "
    query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
            -[r:KILLED]->(a2:Avatar)-[:IS]-(h:Hero)\
            RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
    top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
    for hero in top_heroes_json:
        output += "Hero " + str(hero['h.hero_id']) + " was killed " +\
                 str(hero['r.weight']) + " times, "

    output += "Your healed heroes are: "
    query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
            -[r:HEALED]->(a2:Avatar)-[:IS]-(h:Hero)\
            RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
    top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
    for hero in top_heroes_json:
        output += "Hero " + str(hero['h.hero_id']) + " was healed " +\
                 str(hero['r.weight']) + " times, "

    output += "Your damaged heroes are: "
    query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
            -[r:DAMAGED]->(a2:Avatar)-[:IS]-(h:Hero)\
            RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
    top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
    for hero in top_heroes_json:
        output += "Hero " + str(hero['h.hero_id']) + " was damaged " +\
                 str(hero['r.weight']) + " times, "
    return output

@app.callback(
    dash.dependencies.Output('team', 'children'),
    [dash.dependencies.Input('hero-slider','value'),
        dash.dependencies.Input('account-selection','value')]
)
def update_output(hero_id, account_id):
    try:
        heroes = {}
        query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
                -[r:WON_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
        top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
        for hero in top_heroes_json:
            hero_id2 = hero['h.hero_id']
            if hero_id != hero_id2:
                if hero_id2 not in heroes:
                    heroes[hero_id2] = 1
                else:
                    heroes[hero_id2] += 1

        query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
                -[r:LOST_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
        top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
        for hero in top_heroes_json:
            hero_id2 = hero['h.hero_id']
            if hero_id != hero_id2:
                if hero_id2 not in heroes:
                    heroes[hero_id2] = 0
                else:
                    heroes[hero_id2] -= 1

        query = "MATCH (a:Avatar{composite_id:'"+str(account_id)+str(hero_id)+"'})\
                -[r:HEALED]->(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN h.hero_id, r.weight ORDER BY r.weight DESC"
        top_heroes_json = json.loads(json.dumps(graph.run(query).data()))
        for hero in top_heroes_json:
            hero_id2 = hero['h.hero_id']
            if hero_id != hero_id2:
                if hero_id2 not in heroes:
                    heroes[hero_id2] = 2
                else:
                    heroes[hero_id2] += 2
        output = "Factoring in wins, losses, and heals, your team should have the heroes: "
        if heroes == {}:
            return "Check hero_id selection with slider to match top heroes"
        output += str(sorted(heroes, key=heroes.get, reverse=True)[:4])
        return output
    except e as Exception:
        return repr(e)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True)
