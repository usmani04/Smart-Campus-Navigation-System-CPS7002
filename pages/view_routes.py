import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

CSV_PATH = "data/routes.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read ------------------
def read_routes():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=["id", "start_location", "end_location", "distance_m", "accessible"])

# ------------------ Table Generation ------------------
def generate_routes_table(df):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Start", className="p-2 bg-light border"),
        html.Th("End", className="p-2 bg-light border"),
        html.Th("Distance (m)", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
    ])

    rows = []
    for _, row in df.iterrows():
        accessible_text = "✅ Yes" if row.accessible else "❌ No"
        accessible_color = BLUE if row.accessible else "red"

        rows.append(
            html.Tr([
                html.Td(row.id, className="p-2 border"),
                html.Td(row.start_location, className="p-2 border"),
                html.Td(row.end_location, className="p-2 border"),
                html.Td(row.distance_m, className="p-2 border"),
                html.Td(html.Span(accessible_text, style={'color': accessible_color, 'fontWeight': 'bold'}), className="p-2 border"),
            ])
        )

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")

# ------------------ Layout ------------------
def view_routes_layout():
    df = read_routes()
    return dbc.Container([

        # Search
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
                # Table
                html.Div(id="table-routes", children=generate_routes_table(df))
            ]
        ),

    ], fluid=True)

# ------------------ Callbacks ------------------
@callback(
    Output("table-routes", "children"),
    Input("search-routes", "value"),
    prevent_initial_call=True
)
def search_routes(text):
    df = read_routes()
    if not text:
        return generate_routes_table(df)
    t = text.lower()
    df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
    return generate_routes_table(df)
