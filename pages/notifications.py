import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# ------------------ Config ------------------
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read / Write ------------------
def read_notifications():
    if os.path.exists(NOTIF_CSV_PATH):
        return pd.read_csv(NOTIF_CSV_PATH)
    return pd.DataFrame(columns=["id", "user_id", "message", "delivered"])


def save_notifications(df):
    df.to_csv(NOTIF_CSV_PATH, index=False)

# ------------------ Table Generation ------------------
def generate_notifications_table(df):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("User ID", className="p-2 bg-light border"),
        html.Th("Message", className="p-2 bg-light border"),
        html.Th("Delivered", className="p-2 bg-light border"),
        html.Th("Actions", className="p-2 bg-light border"),
    ])

    rows = []
    for _, row in df.iterrows():
        delivered_text = "✅ Yes" if row.delivered else "❌ No"
        delivered_color = BLUE if row.delivered else "red"

        rows.append(
            html.Tr([
                html.Td(row.id, className="p-2 border"),
                html.Td(row.user_id, className="p-2 border"),
                html.Td(row.message, className="p-2 border"),
                html.Td(
                    html.Span(
                        delivered_text,
                        style={"color": delivered_color, "fontWeight": "bold"}
                    ),
                    className="p-2 border"
                ),
                html.Td([
                    dbc.Button(
                        "Edit",
                        id={"type": "edit-notif", "index": int(row.id)},
                        color="warning",
                        size="sm",
                        className="me-1"
                    ),
                    dbc.Button(
                        "Delete",
                        id={"type": "delete-notif", "index": int(row.id)},
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
def notifications_layout():
    df = read_notifications()

    return dbc.Container([
        # Add / Edit Form
        dbc.Card([
            dbc.CardBody([
                html.H3("Add / Edit Notification", className="mb-3"),
                dcc.Store(id="edit-notif-id", data=None),

                dbc.Row([
                    dbc.Col(
                        dcc.Input(
                            id="notif-user-id",
                            placeholder="User ID",
                            type="number",
                            value="",
                            className="form-control"
                        ),
                        md=3
                    ),
                    dbc.Col(
                        dcc.Input(
                            id="notif-message",
                            placeholder="Message",
                            value="",
                            className="form-control"
                        ),
                        md=6
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="notif-delivered",
                            options=[
                                {"label": "Delivered", "value": True},
                                {"label": "Not Delivered", "value": False}
                            ],
                            value=None,
                            placeholder="Delivered"
                        ),
                        md=3
                    )
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(
                        dbc.Button(
                            "Add",
                            id="add-notif-btn",
                            n_clicks=0,
                            color="primary",
                            className="me-2"
                        ),
                        width="auto"
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Reset",
                            id="reset-notif-btn",
                            n_clicks=0,
                            color="secondary"
                        ),
                        width="auto"
                    )
                ], className="justify-content-end"),

                html.Div(id="msg-notif", className="mt-2")
            ])
        ], className="mb-4 shadow-sm"),

        # Search

        dbc.Card(
                className="p-3 mb-4 shadow-sm",
                children=[
                    dbc.Row([
                        dbc.Col(
                            dcc.Input(
                                id="search-notif",
                                placeholder="Search notifications...",
                                value="",
                                className="form-control mb-3",
                                style={"maxWidth": "300px"}
                            )
                        )
                    ]),
                    # Table
                    html.Div(id="table-notif", children=generate_notifications_table(df))
                ]
            ),
        

    ], fluid=True)

# ------------------ Callbacks ------------------

# Delete
@callback(
    Output("table-notif", "children", allow_duplicate=True),
    Input({"type": "delete-notif", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_notification(clicks):
    if not any(clicks):
        raise PreventUpdate

    ctx = dash.callback_context
    notif_id = ctx.triggered_id["index"]

    df = read_notifications()
    df = df[df.id != notif_id]
    save_notifications(df)

    return generate_notifications_table(df)

# Edit (Prefill Form)
@callback(
    Output("notif-user-id", "value", allow_duplicate=True),
    Output("notif-message", "value", allow_duplicate=True),
    Output("notif-delivered", "value", allow_duplicate=True),
    Output("add-notif-btn", "children", allow_duplicate=True),
    Output("edit-notif-id", "data", allow_duplicate=True),
    Input({"type": "edit-notif", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def edit_notification(clicks):
    if not any(clicks):
        raise PreventUpdate

    ctx = dash.callback_context
    notif_id = ctx.triggered_id["index"]

    df = read_notifications()
    r = df[df.id == notif_id].iloc[0]

    return r.user_id, r.message, r.delivered, "Update", notif_id

# Reset Form
@callback(
    Output("notif-user-id", "value", allow_duplicate=True),
    Output("notif-message", "value", allow_duplicate=True),
    Output("notif-delivered", "value", allow_duplicate=True),
    Output("add-notif-btn", "children", allow_duplicate=True),
    Output("edit-notif-id", "data", allow_duplicate=True),
    Output("msg-notif", "children", allow_duplicate=True),
    Input("reset-notif-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_notif_form(_):
    return "", "", None, "Add", None, ""

# Add / Update Notification
@callback(
    Output("table-notif", "children", allow_duplicate=True),
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

    df = read_notifications()

    if edit_id is not None:
        df.loc[df.id == edit_id, ["user_id", "message", "delivered"]] = [
            user_id, message, delivered
        ]
        msg = "Notification updated"
    else:
        new_id = int(df.id.max()) + 1 if not df.empty else 1
        df = pd.concat([
            df,
            pd.DataFrame([{
                "id": new_id,
                "user_id": user_id,
                "message": message,
                "delivered": delivered
            }])
        ], ignore_index=True)
        msg = "Notification added"

    save_notifications(df)
    return generate_notifications_table(df), msg

# Search
@callback(
    Output("table-notif", "children", allow_duplicate=True),
    Input("search-notif", "value"),
    prevent_initial_call=True
)
def search_notifications(text):
    df = read_notifications()
    if not text:
        return generate_notifications_table(df)

    t = text.lower()
    df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
    return generate_notifications_table(df)
