import dash
from dash import html, dcc, Input, Output, State, callback
import pandas as pd

BLUE = "#0B63C5"
LIGHT = "#F4F9FF"
WHITE = "#FFFFFF"
GREEN = "#28a745"
RED = "#dc3545"

def load_routes():
    try:
        df = pd.read_csv("data/routes.csv")
        return df
    except:
        return pd.DataFrame(columns=['id', 'start_location', 'end_location', 'distance_m', 'accessible'])

def layout():
    df = load_routes()
    
    locations = []
    if not df.empty:
        locations = sorted(set(df['start_location'].tolist() + df['end_location'].tolist()))
    
    return html.Div(
        style={
            'backgroundColor': LIGHT,
            'minHeight': '100vh',
            'padding': '20px'
        },
        children=[
            html.H1("📍 Campus Route Finder", 
                   style={'color': BLUE, 'marginBottom': '20px'}),
            
           
            html.Div(
                style={
                    'backgroundColor': WHITE,
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                    'marginBottom': '30px'
                },
                children=[
                    html.H3("Find Route", style={'color': BLUE, 'marginBottom': '20px'}),
                    
                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': '1fr 1fr',
                            'gap': '20px',
                            'marginBottom': '20px'
                        },
                        children=[
                            html.Div(
                                children=[
                                    html.Label("From", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                                    dcc.Dropdown(
                                        id='start-location',
                                        options=[{'label': loc, 'value': loc} for loc in locations],
                                        placeholder='Select start location...',
                                        
                                    )
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.Label("To", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                                    dcc.Dropdown(
                                        id='end-location',
                                        options=[{'label': loc, 'value': loc} for loc in locations],
                                        placeholder='Select destination...',
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    html.Div(
                        style={
                            'display': 'flex',
                            'gap': '20px',
                            'marginBottom': '20px',
                            'alignItems': 'flex-end'
                        },
                        children=[
                            html.Div(
                                style={'flex': '1'},
                                children=[
                                    html.Label("Filters", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                                    dcc.Checklist(
                                        id='filter-accessible',
                                        options=[
                                            {'label': ' Show only accessible routes', 'value': 'yes'}
                                        ],
                                        value=[]
                                    )
                                ]
                            ),
                            html.Button(
                                'Find Routes',
                                id='find-btn',
                                style={
                                    'backgroundColor': BLUE,
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '10px 25px',
                                    'borderRadius': '6px',
                                    'cursor': 'pointer',
                                    'fontSize': '16px',
                                    'height': '40px'
                                }
                            )
                        ]
                    ),
                    
                    html.Div(id='route-result', style={'marginTop': '20px'})
                ]
            ),
            
            html.Div(
                style={
                    'backgroundColor': WHITE,
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
                },
                children=[
                    html.Div(
                        style={
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'alignItems': 'center',
                            'marginBottom': '20px'
                        },
                        children=[
                            html.H3("All Routes", style={'color': BLUE, 'margin': '0'}),
                            html.Div(
                                style={'display': 'flex', 'gap': '10px', 'alignItems': 'center'},
                                children=[
                                    dcc.Input(
                                        id='search-routes',
                                        placeholder='Search routes...',
                                        style={
                                            'padding': '8px 12px',
                                            'border': f'1px solid {BLUE}',
                                            'borderRadius': '6px',
                                            'width': '200px'
                                        }
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    html.Div(id='routes-table')
                ]
            )
        ]
    )

def generate_table(df):
    if df.empty:
        return html.P("No routes data available.", style={'color': '#666'})
    

    header = html.Tr([
        html.Th("ID", style={'padding': '12px', 'textAlign': 'left', 'backgroundColor': LIGHT, 'borderBottom': '2px solid #ddd'}),
        html.Th("Start", style={'padding': '12px', 'textAlign': 'left', 'backgroundColor': LIGHT, 'borderBottom': '2px solid #ddd'}),
        html.Th("End", style={'padding': '12px', 'textAlign': 'left', 'backgroundColor': LIGHT, 'borderBottom': '2px solid #ddd'}),
        html.Th("Distance (m)", style={'padding': '12px', 'textAlign': 'left', 'backgroundColor': LIGHT, 'borderBottom': '2px solid #ddd'}),
        html.Th("Accessible", style={'padding': '12px', 'textAlign': 'left', 'backgroundColor': LIGHT, 'borderBottom': '2px solid #ddd'})
    ])

    rows = []
    for i, row in df.iterrows():
        accessible_text = "✅ Yes" if row['accessible'] else "❌ No"
        accessible_color = GREEN if row['accessible'] else RED
        
        rows.append(
            html.Tr(
                style={'backgroundColor': '#FAFAFA' if i % 2 == 0 else WHITE},
                children=[
                    html.Td(row['id'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                    html.Td(row['start_location'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                    html.Td(row['end_location'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                    html.Td(row['distance_m'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                    html.Td(
                        html.Span(accessible_text, style={'color': accessible_color, 'fontWeight': 'bold'}),
                        style={'padding': '10px', 'borderBottom': '1px solid #eee'}
                    )
                ]
            )
        )
    
    return html.Table(
        [header] + rows,
        style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'fontSize': '14px'
        }
    )

@callback(
    Output('routes-table', 'children'),
    Input('search-routes', 'value'),
    Input('filter-accessible', 'value')
)
def update_table(search_text, filter_value):
    df = load_routes()
    
    if df.empty:
        return html.P("No routes data available.", style={'color': '#666'})
    
    if 'yes' in filter_value:
        df = df[df['accessible'] == True]
    
    if search_text:
        search_text = search_text.lower()
        df = df[
            df['start_location'].str.lower().str.contains(search_text) |
            df['end_location'].str.lower().str.contains(search_text)
        ]
    
    return generate_table(df)

@callback(
    Output('route-result', 'children'),
    Input('find-btn', 'n_clicks'),
    State('start-location', 'value'),
    State('end-location', 'value'),
    State('filter-accessible', 'value')
)
def find_route(n_clicks, start, end, filter_value):
    if not n_clicks:
        return ""
    
    if not start or not end:
        return html.P("Please select both start and end locations.", style={'color': 'red', 'fontWeight': 'bold'})
    
    df = load_routes()
    
    if df.empty:
        return html.P("No routes data available.", style={'color': 'red'})
    
    if 'yes' in filter_value:
        df = df[df['accessible'] == True]
    
    direct_routes = df[(df['start_location'] == start) & (df['end_location'] == end)]
    
    if direct_routes.empty:
        return html.Div([
            html.H4(f"❌ No direct route found from {start} to {end}", 
                   style={'color': 'red', 'marginBottom': '10px'}),
            html.P("Try selecting different locations or remove the 'accessible only' filter.", 
                  style={'color': '#666'})
        ])
    
    # Find shortest route
    shortest_idx = direct_routes['distance_m'].idxmin()
    shortest_route = direct_routes.loc[shortest_idx]
    
    return html.Div([
        html.H4(f"✅ Route Found: {start} → {end}", 
               style={'color': GREEN, 'marginBottom': '15px'}),
        
        html.Div(
            style={
                'backgroundColor': '#f0f8ff',
                'padding': '15px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'borderLeft': f'4px solid {GREEN if shortest_route["accessible"] else RED}'
            },
            children=[
                html.H5("🏆 Shortest Route", style={'marginTop': '0', 'color': BLUE}),
                html.P(f"📍 Route ID: {shortest_route['id']}"),
                html.P(f"📏 Distance: {shortest_route['distance_m']} meters"),
                html.P(f"♿ Accessible: {'✅ Yes' if shortest_route['accessible'] else '❌ No'}"),
            ]
        ),
        
        
        html.H5("All Available Routes:", style={'marginBottom': '10px'}),
        html.Ul(
            children=[
                html.Li(
                    style={'marginBottom': '5px', 'padding': '5px', 'backgroundColor': '#f9f9f9'},
                    children=[
                        html.Span(f"Route {row['id']}: ", style={'fontWeight': 'bold'}),
                        html.Span(f"{row['distance_m']}m"),
                        html.Span(f" ({'✅ Accessible' if row['accessible'] else '❌ Not Accessible'})", 
                                style={'color': GREEN if row['accessible'] else RED, 'marginLeft': '10px'})
                    ]
                )
                for _, row in direct_routes.iterrows()
            ],
            style={'listStyle': 'none', 'padding': '0'}
        )
    ])