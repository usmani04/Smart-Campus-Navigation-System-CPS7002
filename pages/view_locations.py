import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# ------------------ Config ------------------
LOC_CSV_PATH = "data/locations.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read/Write ------------------
def read_locations():
    if os.path.exists(LOC_CSV_PATH):
        return pd.read_csv(LOC_CSV_PATH)
    return pd.DataFrame(columns=["id", "name", "building", "floor", "accessible"])

# ------------------ Table Generation ------------------
def generate_locations_table(df):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Name", className="p-2 bg-light border"),
        html.Th("Building", className="p-2 bg-light border"),
        html.Th("Floor", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
    ])

    rows = []
    for _, row in df.iterrows():
        accessible_text = "✅ Yes" if row.accessible else "❌ No"
        accessible_color = BLUE if row.accessible else "red"

        rows.append(
            html.Tr([
                html.Td(row.id, className="p-2 border"),
                html.Td(row.name, className="p-2 border"),
                html.Td(row.building, className="p-2 border"),
                html.Td(row.floor, className="p-2 border"),
                html.Td(
                    html.Span(accessible_text, style={'color': accessible_color, 'fontWeight': 'bold'}),
                    className="p-2 border"
                ),
            ])
        )

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")

# ------------------ Layout ------------------
def view_locations_layout():
    df = read_locations()

    return dbc.Container([

        dbc.Card(
            className="p-3 mb-4 shadow-sm",
            children=[
                # Search
                dbc.Row([
                    dbc.Col(
                        dcc.Input(
                            id="search-loc",
                            placeholder="Search locations...",
                            value="",
                            className="form-control mb-3",
                            style={"maxWidth":"300px"}
                        )
                    )
                ]),
                # Table
                html.Div(id="table-loc", children=generate_locations_table(df))
            ]
        ),

    ], fluid=True)

# ------------------ Callbacks ------------------
@callback(
    Output("table-loc", "children"),
    Input("search-loc", "value")
)
def search_locations(text):
    df = read_locations()
    if not text:
        return generate_locations_table(df)

    t = text.lower()
    df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
    return generate_locations_table(df)
