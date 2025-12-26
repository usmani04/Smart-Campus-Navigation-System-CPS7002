import os
import csv
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

CSV_PATH = "data/routes.csv"
BLUE = "#2f80ed"

def read_routes():
    routes = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                routes.append({
                    'id': int(row['id']),
                    'start_location': row['start_location'],
                    'end_location': row['end_location'],
                    'distance_m': float(row['distance_m']),
                    'accessible': row['accessible'].lower() == 'true'
                })
    return routes

def generate_routes_table(routes):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Start", className="p-2 bg-light border"),
        html.Th("End", className="p-2 bg-light border"),
        html.Th("Distance (m)", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
    ])

    rows = []
    for r in routes:
        accessible_text = "✅ Yes" if r['accessible'] else "❌ No"
        accessible_color = BLUE if r['accessible'] else "red"

        rows.append(
            html.Tr([
                html.Td(r['id'], className="p-2 border"),
                html.Td(r['start_location'], className="p-2 border"),
                html.Td(r['end_location'], className="p-2 border"),
                html.Td(r['distance_m'], className="p-2 border"),
                html.Td(html.Span(accessible_text, style={'color': accessible_color, 'fontWeight': 'bold'}), className="p-2 border"),
            ])
        )

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")


def view_routes_layout():
    routes = read_routes()
    return dbc.Container([


        dbc.Card(
            className="p-3 mb-4 shadow-sm",
            children=[
                dbc.Row([
                    dbc.Col(
                        dcc.Input(
                            id="search-routes",
                            placeholder="Search routes...",
                            value="",
                            className="form-control mb-3",
                            style={"maxWidth": "300px"}
                        )
                    )
                ]),
              
                html.Div(id="table-routes", children=generate_routes_table(routes))
            ]
        ),

    ], fluid=True)


@callback(
    Output("table-routes", "children"),
    Input("search-routes", "value"),
    prevent_initial_call=True
)
def search_routes(text):
    routes = read_routes()
    if not text:
        return generate_routes_table(routes)
    t = text.lower()
    filtered = [r for r in routes if t in str(r).lower()]
    return generate_routes_table(filtered)
