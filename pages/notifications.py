import os
import csv
import dash
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from flask import session
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

def read_notifications():
    if os.path.exists(NOTIF_CSV_PATH):
        with open(NOTIF_CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            notifications = []
            for row in reader:
                notifications.append({
                    "id": int(row["id"]),
                    "user_id": int(row["user_id"]),
                    "message": row["message"],
                    "delivered": row["delivered"].lower() == "true"
                })
            return notifications
    return []

def save_notifications(notifications):
    with open(NOTIF_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["id", "user_id", "message", "delivered"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for n in notifications:
            writer.writerow({
                "id": n["id"],
                "user_id": n["user_id"],
                "message": n["message"],
                "delivered": n["delivered"]
            })

def generate_notifications_table(notifications, is_admin=False):
    header_cells = [
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("User ID", className="p-2 bg-light border"),
        html.Th("Message", className="p-2 bg-light border"),
        html.Th("Delivered", className="p-2 bg-light border"),
    ]
    if is_admin:
        header_cells.append(html.Th("Actions", className="p-2 bg-light border"))

    header = html.Tr(header_cells)
    rows = []

    for row in notifications:
        delivered_text = "✅ Yes" if row["delivered"] else "❌ No"
        delivered_color = BLUE if row["delivered"] else "red"

        row_cells = [
            html.Td(row["id"], className="p-2 border"),
            html.Td(row["user_id"], className="p-2 border"),
            html.Td(row["message"], className="p-2 border"),
            html.Td(
                html.Span(delivered_text, style={"color": delivered_color, "fontWeight": "bold"}),
                className="p-2 border"
            )
        ]

        if is_admin:
            row_cells.append(
                html.Td([
                    dbc.Button(
                        "Edit",
                        id={"type": "edit-notif", "index": row["id"]},
                        color="warning",
                        size="sm",
                        className="me-1"
                    ),
                    dbc.Button(
                        "Delete",
                        id={"type": "delete-notif", "index": row["id"]},
                        color="danger",
                        size="sm"
                    )
                ])
            )
        rows.append(html.Tr(row_cells))

    return dbc.Table([header] + rows, bordered=False, hover=True, responsive=True, striped=True, className="mb-0")

def notifications_layout():
    notifications = read_notifications()
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3("Add / Edit Notification", className="mb-3"),
                dcc.Store(id="edit-notif-id", data=None),
                dbc.Row([
                    dbc.Col(
                        dcc.Input(id="notif-user-id", placeholder="User ID", type="number", value=None, className="form-control"),
                        md=3
                    ),
                    dbc.Col(
                        dcc.Input(id="notif-message", placeholder="Message", value="", className="form-control"),
                        md=6
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="notif-delivered",
                            options=[{"label": "Delivered", "value": True}, {"label": "Not Delivered", "value": False}],
                            value=None,
                            placeholder="Delivered"
                        ),
                        md=3
                    )
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(dbc.Button("Add", id="add-notif-btn", n_clicks=0, color="primary", className="me-2"), width="auto"),
                    dbc.Col(dbc.Button("Reset", id="reset-notif-btn", n_clicks=0, color="secondary"), width="auto")
                ], className="justify-content-end"),
                html.Div(id="msg-notif", className="mt-2")
            ])
        ], className="mb-4 shadow-sm"),
        dbc.Card(className="p-3 mb-4 shadow-sm", children=[
            dbc.Row([
                dbc.Col(
                    dcc.Input(id="manage-search-notif", placeholder="Search notifications...", value=None, className="form-control mb-3", style={"maxWidth": "300px"})
                )
            ]),
            html.Div(id="manage-table-notif", children=generate_notifications_table(notifications, is_admin=True))
        ]),
    ], fluid=True)

@callback(
    Output("manage-table-notif", "children", allow_duplicate=True),
    Input({"type": "delete-notif", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_notification(clicks):
    if not any(clicks):
        raise PreventUpdate

    ctx = dash.callback_context
    notif_id = ctx.triggered_id["index"]
    notifications = read_notifications()
    notifications = [n for n in notifications if n["id"] != notif_id]
    save_notifications(notifications)
    return generate_notifications_table(notifications, is_admin=True)

@callback(
    Output("notif-user-id", "value"),
    Output("notif-message", "value"),
    Output("notif-delivered", "value"),
    Output("add-notif-btn", "children"),
    Output("edit-notif-id", "data"),
    Output("msg-notif", "children", allow_duplicate=True),
    Input({"type": "edit-notif", "index": ALL}, "n_clicks"),
    Input("reset-notif-btn", "n_clicks"),
    prevent_initial_call=True
)
def edit_reset_notification(edit_clicks, reset_click):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]["prop_id"]
    if "edit-notif" in trigger_id:
        if not any(edit_clicks):
            raise PreventUpdate
        notif_id = ctx.triggered_id["index"]
        notifications = read_notifications()
        row = next((n for n in notifications if n["id"] == notif_id), None)
        if row is None:
            raise PreventUpdate
        return row["user_id"], row["message"], row["delivered"], "Update", notif_id, ""
    elif trigger_id == "reset-notif-btn.n_clicks":
        return None, "", None, "Add", None, ""
    raise PreventUpdate

@callback(
    Output("manage-table-notif", "children", allow_duplicate=True),
    Output("msg-notif", "children"),
    Input("add-notif-btn", "n_clicks"),
    State("notif-user-id", "value"),
    State("notif-message", "value"),
    State("notif-delivered", "value"),
    State("edit-notif-id", "data"),
    prevent_initial_call=True
)
def save_notification(_, user_id, message, delivered, edit_id):
    if not all([user_id, message]) or delivered is None:
        return dash.no_update, "Please fill all fields"

    notifications = read_notifications()

    if edit_id is not None:
        for n in notifications:
            if n["id"] == edit_id:
                n["user_id"] = user_id
                n["message"] = message
                n["delivered"] = delivered
        msg = "Notification updated successfully"
    else:
        new_id = max([n["id"] for n in notifications], default=0) + 1
        notifications.append({"id": new_id, "user_id": user_id, "message": message, "delivered": delivered})
        msg = "Notification added successfully"

    save_notifications(notifications)
    return generate_notifications_table(notifications, is_admin=True), msg

@callback(
    Output("manage-table-notif", "children", allow_duplicate=True),
    Input("manage-search-notif", "value"),
    prevent_initial_call=True
)
def search_notifications(text):
    notifications = read_notifications()
    if not text:
        return generate_notifications_table(notifications, is_admin=True)
    t = text.lower()
    filtered = []
    for n in notifications:
        if any(t in str(v).lower() for v in n.values()):
            filtered.append(n)
    return generate_notifications_table(filtered, is_admin=True)
