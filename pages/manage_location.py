import os
import csv
import dash
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

LOC_CSV_PATH = "data/locations.csv"
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

def read_locations():
    locations = []
    if os.path.exists(LOC_CSV_PATH):
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

def save_locations(locations):
    with open(LOC_CSV_PATH, 'w', newline='') as f:
        if locations:
            writer = csv.DictWriter(f, fieldnames=locations[0].keys())
            writer.writeheader()
            for loc in locations:
                loc_copy = loc.copy()
                loc_copy['accessible'] = str(loc_copy['accessible'])
                writer.writerow(loc_copy)

def add_notification(message, user_id=1):
    notifications = []
    if os.path.exists(NOTIF_CSV_PATH):
        with open(NOTIF_CSV_PATH, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                notifications.append({
                    'id': int(row['id']),
                    'user_id': int(row['user_id']),
                    'message': row['message'],
                    'delivered': row['delivered'].lower() == 'true'
                })
    new_id = max([n['id'] for n in notifications], default=0) + 1
    notifications.append({
        'id': new_id,
        'user_id': user_id,
        'message': message,
        'delivered': False
    })
    with open(NOTIF_CSV_PATH, 'w', newline='') as f:
        if notifications:
            writer = csv.DictWriter(f, fieldnames=notifications[0].keys())
            writer.writeheader()
            for n in notifications:
                n_copy = n.copy()
                n_copy['delivered'] = str(n_copy['delivered'])
                writer.writerow(n_copy)

def generate_locations_table(locations):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Name", className="p-2 bg-light border"),
        html.Th("Building", className="p-2 bg-light border"),
        html.Th("Floor", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
        html.Th("Actions", className="p-2 bg-light border"),
    ])

    rows = []
    for loc in locations:
        id_val = loc["id"]
        name_val = loc["name"]
        building_val = loc["building"]
        floor_val = loc["floor"]
        accessible_val = loc["accessible"]

        accessible_text = "✅ Yes" if accessible_val else "❌ No"
        accessible_color = BLUE if accessible_val else "red"

        rows.append(
            html.Tr([
                html.Td(id_val, className="p-2 border"),
                html.Td(name_val, className="p-2 border"),
                html.Td(building_val, className="p-2 border"),
                html.Td(floor_val, className="p-2 border"),
                html.Td(
                    html.Span(
                        accessible_text,
                        style={"color": accessible_color, "fontWeight": "bold"}
                    ),
                    className="p-2 border"
                ),
                html.Td([
                    dbc.Button(
                        "Edit",
                        id={"type": "edit-loc", "index": id_val},
                        color="warning",
                        size="sm",
                        className="me-1"
                    ),
                    dbc.Button(
                        "Delete",
                        id={"type": "delete-loc", "index": id_val},
                        color="danger",
                        size="sm"
                    )
                ])
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

def locations_layout():
    locations = read_locations()

    return dbc.Container([

        dbc.Toast(
            id="loc-toast",
            header="Success",
            is_open=False,
            dismissable=True,
            duration=3000,
            icon="success",
            style={
                "position": "fixed",
                "top": 20,
                "right": 20,
                "width": 350,
                "zIndex": 9999
            }
        ),

        dbc.Card([
            dbc.CardBody([
                html.H3("Add / Edit Location", className="mb-3"),
                dcc.Store(id="edit-loc-id", data=None),

                dbc.Row([
                    dbc.Col(dcc.Input(id="loc-name", placeholder="Name", value="", className="form-control"), md=3),
                    dbc.Col(dcc.Input(id="loc-building", placeholder="Building", value="", className="form-control"), md=3),
                    dbc.Col(dcc.Input(id="loc-floor", placeholder="Floor", value="", className="form-control"), md=3),
                    dbc.Col(dcc.Dropdown(
                        id="loc-accessible",
                        options=[
                            {"label": "Accessible", "value": True},
                            {"label": "Not Accessible", "value": False}
                        ],
                        value=None,
                        placeholder="Accessible"
                    ), md=3)
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(dbc.Button("Add", id="add-loc-btn", n_clicks=0, color="primary", className="me-2"), width="auto"),
                    dbc.Col(dbc.Button("Reset", id="reset-loc-btn", n_clicks=0, color="secondary"), width="auto")
                ], className="justify-content-end"),
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card(
            className="p-3 mb-4 shadow-sm",
            children=[
                dbc.Row([
                    dbc.Col(
                        dcc.Input(
                            id="manage-search-loc",
                            placeholder="Search locations...",
                            value="",
                            className="form-control mb-3",
                            style={"maxWidth": "300px"}
                        )
                    )
                ]),
                html.Div(id="manage-table-loc", children=generate_locations_table(locations))
            ]
        ),

    ], fluid=True)

@callback(
    Output("manage-table-loc", "children", allow_duplicate=True),
    Output("loc-toast", "children", allow_duplicate=True),
    Output("loc-toast", "is_open", allow_duplicate=True),
    Input({"type": "delete-loc", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_location(clicks):
    if not any(clicks):
        raise PreventUpdate

    loc_id = dash.callback_context.triggered_id["index"]

    locations = read_locations()
    loc_name = next(loc['name'] for loc in locations if loc['id'] == loc_id)

    locations = [loc for loc in locations if loc['id'] != loc_id]
    save_locations(locations)

    add_notification(f"Location '{loc_name}' deleted")

    return generate_locations_table(locations), "Location deleted successfully", True

@callback(
    Output("loc-name", "value", allow_duplicate=True),
    Output("loc-building", "value", allow_duplicate=True),
    Output("loc-floor", "value", allow_duplicate=True),
    Output("loc-accessible", "value", allow_duplicate=True),
    Output("add-loc-btn", "children", allow_duplicate=True),
    Output("edit-loc-id", "data", allow_duplicate=True),
    Input({"type": "edit-loc", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def edit_location(clicks):
    if not any(clicks):
        raise PreventUpdate

    loc_id = dash.callback_context.triggered_id["index"]
    locations = read_locations()
    r = next(loc for loc in locations if loc['id'] == loc_id)

    return r["name"], r["building"], r["floor"], r["accessible"], "Update", loc_id

@callback(
    Output("loc-name", "value", allow_duplicate=True),
    Output("loc-building", "value", allow_duplicate=True),
    Output("loc-floor", "value", allow_duplicate=True),
    Output("loc-accessible", "value", allow_duplicate=True),
    Output("add-loc-btn", "children", allow_duplicate=True),
    Output("edit-loc-id", "data", allow_duplicate=True),
    Input("reset-loc-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_loc_form(_):
    return "", "", "", None, "Add", None

@callback(
    Output("manage-table-loc", "children", allow_duplicate=True),
    Output("loc-toast", "children", allow_duplicate=True),
    Output("loc-toast", "is_open", allow_duplicate=True),
    Input("add-loc-btn", "n_clicks"),
    State("loc-name", "value"),
    State("loc-building", "value"),
    State("loc-floor", "value"),
    State("loc-accessible", "value"),
    State("edit-loc-id", "data"),
    prevent_initial_call=True
)
def save_location(_, name, building, floor, accessible, edit_id):
    if not all([name, building, floor]) or accessible is None:
        raise PreventUpdate

    locations = read_locations()

    if edit_id is not None:
        for loc in locations:
            if loc['id'] == edit_id:
                loc.update({'name': name, 'building': building, 'floor': int(floor), 'accessible': accessible})
                break
        msg = "Location updated successfully"
        add_notification(f"Location '{name}' updated")
    else:
        new_id = max([loc['id'] for loc in locations], default=0) + 1
        locations.append({
            'id': new_id,
            'name': name,
            'building': building,
            'floor': int(floor),
            'accessible': accessible
        })
        msg = "Location added successfully"
        add_notification(f"New location '{building}, {floor}' added")

    save_locations(locations)

    return generate_locations_table(locations), msg, True

@callback(
    Output("manage-table-loc", "children", allow_duplicate=True),
    Input("manage-search-loc", "value"),
    prevent_initial_call=True
)
def search_locations(text):
    locations = read_locations()
    if not text:
        return generate_locations_table(locations)

    t = text.lower()
    filtered = [loc for loc in locations if t in str(loc).lower()]
    return generate_locations_table(filtered)
