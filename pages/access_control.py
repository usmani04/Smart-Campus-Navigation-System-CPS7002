import dash
from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import dash_bootstrap_components as dbc

BLUE = "#0B63C5"
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
    locations = sorted(set(df['start_location'].tolist() + df['end_location'].tolist())) if not df.empty else []

    return dbc.Container([
        html.H1("📍 Campus Route Finder", className="my-4", style={'color': BLUE}),

        
        dbc.Card([
            dbc.CardBody([
                html.H3("Find Route", className="mb-4", style={'color': BLUE}),

                dbc.Row([
                    dbc.Col([
                        html.Label("From", className="fw-bold"),
                        dcc.Dropdown(
                            id='start-location',
                            options=[{'label': loc, 'value': loc} for loc in locations],
                            placeholder='Select start location...'
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label("To", className="fw-bold"),
                        dcc.Dropdown(
                            id='end-location',
                            options=[{'label': loc, 'value': loc} for loc in locations],
                            placeholder='Select destination...'
                        )
                    ], md=6)
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        html.Label("Filters", className="fw-bold"),
                        dcc.Checklist(
                            id='filter-accessible',
                            options=[{'label': ' Show only accessible routes', 'value': 'yes'}],
                            value=[]
                        )
                    ], md=8),
                    dbc.Col([
                        dbc.Button("Find Routes", id="find-btn", color="primary", className="w-100")
                    ], md=4)
                ], className="mb-3"),

                html.Div(id='route-result')
            ])
        ], className="mb-4 shadow-sm"),

       
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.H3("All Routes", style={'color': BLUE}), md=6),
                    dbc.Col(
                        dcc.Input(
                            id='search-routes',
                            placeholder='Search routes...',
                            className="form-control"
                        ),
                        md=6
                    )
                ], className="mb-3"),

                html.Div(id='routes-table')
            ])
        ], className="shadow-sm")
    ], fluid=True)

def generate_table(df):
    if df.empty:
        return html.P("No routes data available.", className='text-muted')

    header = html.Tr([
        html.Th("ID", className='p-2 bg-light border'),
        html.Th("Start", className='p-2 bg-light border'),
        html.Th("End", className='p-2 bg-light border'),
        html.Th("Distance (m)", className='p-2 bg-light border'),
        html.Th("Accessible", className='p-2 bg-light border')
    ])

    rows = []
    for i, row in df.iterrows():
        accessible_bool = bool(row['accessible'])
        accessible_text = "✅ Yes" if accessible_bool else "❌ No"
        accessible_color = GREEN if accessible_bool else RED

        rows.append(
            html.Tr(
                children=[
                    html.Td(row['id'], className='p-2 border'),
                    html.Td(row['start_location'], className='p-2 border'),
                    html.Td(row['end_location'], className='p-2 border'),
                    html.Td(row['distance_m'], className='p-2 border'),
                    html.Td(
                        html.Span(accessible_text, style={'color': accessible_color, 'fontWeight': 'bold'}),
                        className='p-2 border'
                    )
                ]
            )
        )

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")



@callback(
    Output('routes-table', 'children'),
    Input('search-routes', 'value'),
    Input('filter-accessible', 'value')
)
def update_table(search_text, filter_value):
    df = load_routes()
    if df.empty:
        return html.P("No routes data available.", className='text-muted')

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
        return html.P("Please select both start and end locations.", className='text-danger fw-bold')

    df = load_routes()
    if df.empty:
        return html.P("No routes data available.", className='text-danger')

    if 'yes' in filter_value:
        df = df[df['accessible'] == True]

    direct_routes = df[(df['start_location'] == start) & (df['end_location'] == end)]
    if direct_routes.empty:
        return html.Div([
            html.H4(f"❌ No direct route found from {start} to {end}", className='text-danger mb-2'),
            html.P("Try selecting different locations or remove the 'accessible only' filter.", className='text-muted')
        ])

    shortest_idx = direct_routes['distance_m'].idxmin()
    shortest_route = direct_routes.loc[shortest_idx]

    return html.Div([
        html.H4(f"✅ Route Found: {start} → {end}", className='text-success mb-3'),

        dbc.Card([
            dbc.CardBody([
                html.H5("🏆 Shortest Route", style={'color': BLUE}),
                html.P(f"📍 Route ID: {shortest_route['id']}"),
                html.P(f"📏 Distance: {shortest_route['distance_m']} meters"),
                html.P(f"♿ Accessible: {'✅ Yes' if shortest_route['accessible'] else '❌ No'}"),
            ])
        ], className="mb-3 border-start border-4",
           style={'borderColor': GREEN if shortest_route['accessible'] else RED}),

        html.H5("All Available Routes:", className='mb-2'),
        html.Ul([
            html.Li([
                html.Span(f"Route {row['id']}: ", className='fw-bold'),
                html.Span(f"{row['distance_m']}m"),
                html.Span(f" ({'✅ Accessible' if bool(row['accessible']) else '❌ Not Accessible'})",
                          style={'color': GREEN if bool(row['accessible']) else RED, 'marginLeft': '10px'})
            ], className='p-2 bg-light mb-1') for _, row in direct_routes.iterrows()
        ], className='list-unstyled')
    ])
