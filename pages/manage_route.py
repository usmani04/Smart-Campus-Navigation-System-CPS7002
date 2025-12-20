import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

CSV_PATH = "data/routes.csv"
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read / Write ------------------
def read_routes():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=["id", "start_location", "end_location", "distance_m", "accessible"])

def save_routes(df):
    df.to_csv(CSV_PATH, index=False)

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

# ------------------ Table ------------------
def generate_table(df):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Start", className="p-2 bg-light border"),
        html.Th("End", className="p-2 bg-light border"),
        html.Th("Distance (m)", className="p-2 bg-light border"),
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
                html.Td(row.start_location, className="p-2 border"),
                html.Td(row.end_location, className="p-2 border"),
                html.Td(row.distance_m, className="p-2 border"),
                html.Td(
                    html.Span(accessible_text, style={"color": accessible_color, "fontWeight": "bold"}),
                    className="p-2 border"
                ),
                html.Td([
                    dbc.Button("Edit", id={"type": "edit", "index": int(row.id)}, color="warning", size="sm", className="me-1"),
                    dbc.Button("Delete", id={"type": "delete", "index": int(row.id)}, color="danger", size="sm")
                ])
            ])
        )

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")

# ------------------ Layout ------------------
def layout():
    df = read_routes()

    return dbc.Container([

        # ✅ Toast (ADDED – does not replace msg)
        dbc.Toast(
            id="route-toast",
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
                html.H3("Add / Edit Route", className="mb-3"),
                dcc.Store(id="edit-id", data=None),

                dbc.Row([
                    dbc.Col(dcc.Input(id="start", placeholder="Start location", value="", className="form-control"), md=3),
                    dbc.Col(dcc.Input(id="end", placeholder="End location", value="", className="form-control"), md=3),
                    dbc.Col(dcc.Input(id="distance", type="number", placeholder="Distance (m)", value=None, className="form-control"), md=3),
                    dbc.Col(dcc.Dropdown(
                        id="accessible",
                        options=[
                            {"label": "Accessible", "value": True},
                            {"label": "Not Accessible", "value": False},
                        ],
                        value=None,
                        placeholder="Accessible",
                    ), md=3)
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(dbc.Button("Add", id="add-btn", n_clicks=0, color="primary", className="me-2"), width="auto"),
                    dbc.Col(dbc.Button("Reset", id="reset-btn", n_clicks=0, color="secondary"), width="auto")
                ], className="justify-content-end"),

                html.Div(id="msg", className="mt-2")
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card(
            className="p-3 mb-4 shadow-sm",
            children=[
                dbc.Row([
                    dbc.Col(dcc.Input(
                        id="search",
                        placeholder="Search routes...",
                        value="",
                        className="form-control mb-3",
                        style={"maxWidth": "300px"}
                    ))
                ]),
                html.Div(id="table", children=generate_table(df))
            ]
        ),
    ], fluid=True)

# ------------------ Callbacks ------------------

# Delete
@callback(
    Output("table", "children", allow_duplicate=True),
    Output("route-toast", "children", allow_duplicate=True),
    Output("route-toast", "is_open", allow_duplicate=True),
    Input({"type": "delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_route(clicks):
    if not any(clicks):
        raise PreventUpdate

    route_id = dash.callback_context.triggered_id["index"]

    df = read_routes()
    r = df[df.id == route_id].iloc[0]

    df = df[df.id != route_id]
    save_routes(df)

    add_notification(f"Route '{r.start_location} → {r.end_location}' deleted")

    return generate_table(df), "Route deleted successfully", True

# Edit
@callback(
    Output("start", "value", allow_duplicate=True),
    Output("end", "value", allow_duplicate=True),
    Output("distance", "value", allow_duplicate=True),
    Output("accessible", "value", allow_duplicate=True),
    Output("add-btn", "children", allow_duplicate=True),
    Output("edit-id", "data", allow_duplicate=True),
    Input({"type": "edit", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def edit_route(clicks):
    if not any(clicks):
        raise PreventUpdate

    route_id = dash.callback_context.triggered_id["index"]
    df = read_routes()
    r = df[df.id == route_id].iloc[0]

    return r.start_location, r.end_location, r.distance_m, r.accessible, "Update", route_id

# Reset
@callback(
    Output("start", "value", allow_duplicate=True),
    Output("end", "value", allow_duplicate=True),
    Output("distance", "value", allow_duplicate=True),
    Output("accessible", "value", allow_duplicate=True),
    Output("add-btn", "children", allow_duplicate=True),
    Output("edit-id", "data", allow_duplicate=True),
    Output("msg", "children", allow_duplicate=True),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_form(_):
    return "", "", None, None, "Add", None, ""

# Add / Update
@callback(
    Output("table", "children", allow_duplicate=True),
    Output("msg", "children"),
    Output("route-toast", "children", allow_duplicate=True),
    Output("route-toast", "is_open", allow_duplicate=True),
    Input("add-btn", "n_clicks"),
    State("start", "value"),
    State("end", "value"),
    State("distance", "value"),
    State("accessible", "value"),
    State("edit-id", "data"),
    prevent_initial_call=True
)
def save_route(_, s, e, d, a, edit_id):
    if not all([s, e]) or d is None or a is None:
        return dash.no_update, "Please fill all fields", dash.no_update, False

    df = read_routes()

    if edit_id is not None:
        df.loc[df.id == edit_id, ["start_location", "end_location", "distance_m", "accessible"]] = [s, e, d, a]
        msg = "Route updated"
        add_notification(f"Route '{s} → {e}' updated")
    else:
        new_id = int(df.id.max()) + 1 if not df.empty else 1
        df = pd.concat([
            df,
            pd.DataFrame([{
                "id": new_id,
                "start_location": s,
                "end_location": e,
                "distance_m": d,
                "accessible": a
            }])
        ], ignore_index=True)
        msg = "Route added"
        add_notification(f"New route '{s} → {e}' added")

    save_routes(df)
    return generate_table(df), msg, msg, True

# Search
@callback(
    Output("table", "children", allow_duplicate=True),
    Input("search", "value"),
    prevent_initial_call=True
)
def search_routes(text):
    df = read_routes()
    if not text:
        return generate_table(df)

    t = text.lower()
    df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
    return generate_table(df)
