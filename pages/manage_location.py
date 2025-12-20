import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# ------------------ Config ------------------
LOC_CSV_PATH = "data/locations.csv"
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read/Write ------------------
def read_locations():
    if os.path.exists(LOC_CSV_PATH):
        return pd.read_csv(LOC_CSV_PATH)
    return pd.DataFrame(columns=["id", "name", "building", "floor", "accessible"])

def save_locations(df):
    df.to_csv(LOC_CSV_PATH, index=False)

# ------------------ Notification Helper ------------------
def add_notification(message, user_id=1):
    if os.path.exists(NOTIF_CSV_PATH):
        df = pd.read_csv(NOTIF_CSV_PATH)
    else:
        df = pd.DataFrame(columns=["id", "user_id", "message", "delivered"])

    new_id = int(df.id.max()) + 1 if not df.empty else 1

    df = pd.concat([
        df,
        pd.DataFrame([{
            "id": new_id,
            "user_id": user_id,
            "message": message,
            "delivered": False
        }])
    ], ignore_index=True)

    df.to_csv(NOTIF_CSV_PATH, index=False)

# ------------------ Table Generation ------------------
def generate_locations_table(df):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Name", className="p-2 bg-light border"),
        html.Th("Building", className="p-2 bg-light border"),
        html.Th("Floor", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
        html.Th("Actions", className="p-2 bg-light border"),
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
                    html.Span(
                        accessible_text,
                        style={"color": accessible_color, "fontWeight": "bold"}
                    ),
                    className="p-2 border"
                ),
                html.Td([
                    dbc.Button(
                        "Edit",
                        id={"type": "edit-loc", "index": int(row.id)},
                        color="warning",
                        size="sm",
                        className="me-1"
                    ),
                    dbc.Button(
                        "Delete",
                        id={"type": "delete-loc", "index": int(row.id)},
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

# ------------------ Layout ------------------
def locations_layout():
    df = read_locations()

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
                            id="search-loc",
                            placeholder="Search locations...",
                            value="",
                            className="form-control mb-3",
                            style={"maxWidth": "300px"}
                        )
                    )
                ]),
                html.Div(id="table-loc", children=generate_locations_table(df))
            ]
        ),

    ], fluid=True)

# ------------------ Callbacks ------------------

# Delete
@callback(
    Output("table-loc", "children", allow_duplicate=True),
    Output("loc-toast", "children", allow_duplicate=True),
    Output("loc-toast", "is_open", allow_duplicate=True),
    Input({"type": "delete-loc", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_location(clicks):
    if not any(clicks):
        raise PreventUpdate

    loc_id = dash.callback_context.triggered_id["index"]

    df = read_locations()
    loc_name = df[df.id == loc_id]["name"].values[0]

    df = df[df.id != loc_id]
    save_locations(df)

    add_notification(f"Location '{loc_name}' deleted")

    return generate_locations_table(df), "Location deleted successfully", True

# Edit
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
    df = read_locations()
    r = df[df.id == loc_id].iloc[0]

    return r.name, r.building, r.floor, r.accessible, "Update", loc_id

# Reset
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

# Add / Update
@callback(
    Output("table-loc", "children", allow_duplicate=True),
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

    df = read_locations()

    if edit_id is not None:
        df.loc[df.id == edit_id, ["name", "building", "floor", "accessible"]] = [
            name, building, floor, accessible
        ]
        msg = "Location updated successfully"
        add_notification(f"Location '{name}' updated")
    else:
        new_id = int(df.id.max()) + 1 if not df.empty else 1
        df = pd.concat([
            df,
            pd.DataFrame([{
                "id": new_id,
                "name": name,
                "building": building,
                "floor": floor,
                "accessible": accessible
            }])
        ], ignore_index=True)
        msg = "Location added successfully"
        add_notification(f"New location '{building, floor}' added")

    save_locations(df)

    return generate_locations_table(df), msg, True

# Search
@callback(
    Output("table-loc", "children", allow_duplicate=True),
    Input("search-loc", "value"),
    prevent_initial_call=True
)
def search_locations(text):
    df = read_locations()
    if not text:
        return generate_locations_table(df)

    t = text.lower()
    df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
    return generate_locations_table(df)
