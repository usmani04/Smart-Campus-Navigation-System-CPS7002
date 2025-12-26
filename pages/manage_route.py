import os
import csv
import dash
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

CSV_PATH = "data/routes.csv"
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"


def read_routes():
    routes = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                row["id"] = int(row["id"])
                row["distance_m"] = float(row["distance_m"])
                row["accessible"] = row["accessible"].lower() == "true"
                routes.append(row)
    return routes

def save_routes(routes):
    with open(CSV_PATH, "w", newline="") as file:
        if routes:
            writer = csv.DictWriter(file, fieldnames=routes[0].keys())
            writer.writeheader()
            for r in routes:
                writer.writerow(r)


def add_notification(message, user_id=1):
    notifications = []
    if os.path.exists(NOTIF_CSV_PATH):
        with open(NOTIF_CSV_PATH, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                row["id"] = int(row["id"])
                row["user_id"] = int(row["user_id"])
                row["delivered"] = row["delivered"].lower() == "true"
                notifications.append(row)

    new_id = max((n["id"] for n in notifications), default=0) + 1

    notifications.append({
        "id": new_id,
        "user_id": user_id,
        "message": message,
        "delivered": False
    })

    with open(NOTIF_CSV_PATH, "w", newline="") as file:
        if notifications:
            writer = csv.DictWriter(file, fieldnames=notifications[0].keys())
            writer.writeheader()
            for n in notifications:
                writer.writerow(n)


def generate_table(routes):
    if not routes:
        return html.Div("No routes found.")

    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("Start", className="p-2 bg-light border"),
        html.Th("End", className="p-2 bg-light border"),
        html.Th("Distance (m)", className="p-2 bg-light border"),
        html.Th("Accessible", className="p-2 bg-light border"),
        html.Th("Actions", className="p-2 bg-light border"),
    ])

    rows = []
    for r in routes:
        accessible_text = "✅ Yes" if r["accessible"] else "❌ No"
        accessible_color = BLUE if r["accessible"] else "red"

        rows.append(
            html.Tr([
                html.Td(r["id"], className="p-2 border"),
                html.Td(r["start_location"], className="p-2 border"),
                html.Td(r["end_location"], className="p-2 border"),
                html.Td(r["distance_m"], className="p-2 border"),
                html.Td(
                    html.Span(accessible_text, style={"color": accessible_color, "fontWeight": "bold"}),
                    className="p-2 border"
                ),
                html.Td([
                    dbc.Button("Edit", id={"type": "edit", "index": int(r["id"])}, color="warning", size="sm", className="me-1"),
                    dbc.Button("Delete", id={"type": "delete", "index": int(r["id"])}, color="danger", size="sm")
                ])
            ])
        )

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")


def layout():
    routes = read_routes()

    return dbc.Container([

       
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
                html.Div(id="table", children=generate_table(routes))
            ]
        ),
    ], fluid=True)



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

    routes = read_routes()
    r = next((route for route in routes if route["id"] == route_id), None)

    routes = [route for route in routes if route["id"] != route_id]
    save_routes(routes)

    add_notification(f"Route '{r['start_location']} → {r['end_location']}' deleted")

    return generate_table(routes), "Route deleted successfully", True


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
    routes = read_routes()
    r = next((route for route in routes if route["id"] == route_id), None)

    return r["start_location"], r["end_location"], r["distance_m"], r["accessible"], "Update", route_id


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

    routes = read_routes()

    if edit_id is not None:
        for r in routes:
            if r["id"] == edit_id:
                r["start_location"] = s
                r["end_location"] = e
                r["distance_m"] = d
                r["accessible"] = a
                break
        msg = "Route updated"
        add_notification(f"Route '{s} → {e}' updated")
    else:
        new_id = max((r["id"] for r in routes), default=0) + 1
        routes.append({
            "id": new_id,
            "start_location": s,
            "end_location": e,
            "distance_m": d,
            "accessible": a
        })
        msg = "Route added"
        add_notification(f"New route '{s} → {e}' added")

    save_routes(routes)
    return generate_table(routes), msg, msg, True


@callback(
    Output("table", "children", allow_duplicate=True),
    Input("search", "value"),
    prevent_initial_call=True
)
def search_routes(text):
    routes = read_routes()
    if not text:
        return generate_table(routes)

    t = text.lower()
    filtered = [r for r in routes if t in str(r).lower()]
    return generate_table(filtered)
