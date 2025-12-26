import csv
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

LOC_CSV_PATH = "data/locations.csv"
BLUE = "#2f80ed"

def read_locations():
    locations = []
    with open(LOC_CSV_PATH, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({
                'id': int(row['id']),
                'name': row['name'],
                'building': row['building'],
                'floor': int(row['floor']),
                'accessible': row['accessible'].lower() == 'true'
            })
    return locations

def generate_locations_table_view(locations):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Name", className="p-2 bg-light border"),
        html.Th("Building", className="p-2 bg-light border"),
        html.Th("Floor", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
    ])

    rows = []
    for loc in locations:
        accessible = loc['accessible']
        rows.append(
            html.Tr([
                html.Td(loc['id'], className="p-2 border"),
                html.Td(loc['name'], className="p-2 border"),
                html.Td(loc['building'], className="p-2 border"),
                html.Td(loc['floor'], className="p-2 border"),
                html.Td(
                    html.Span(
                        "✅ Yes" if accessible else "❌ No",
                        style={
                            "color": BLUE if accessible else "red",
                            "fontWeight": "bold"
                        }
                    ),
                    className="p-2 border"
                )
            ])
        )

    return dbc.Table(
        [header] + rows,
        bordered=False,
        hover=True,
        responsive=True,
        striped=True,
        className="mb-0"
    )

def view_locations_layout():
    locations = read_locations()

    return dbc.Container([
        dbc.Card(
            className="p-3 mb-4 shadow-sm",
            children=[
                dcc.Input(
                    id="view-search-loc",
                    placeholder="Search locations...",
                    className="form-control mb-3",
                    style={"maxWidth": "300px"}
                ),

                html.Div(
                    id="view-table-loc",
                    children=generate_locations_table_view(locations)
                )
            ]
        )
    ], fluid=True)

@callback(
    Output("view-table-loc", "children"),
    Input("view-search-loc", "value")
)
def search_locations(text):
    locations = read_locations()

    if not text:
        return generate_locations_table_view(locations)

    t = text.lower()
    filtered = [loc for loc in locations if t in str(loc).lower()]
    return generate_locations_table_view(filtered)
