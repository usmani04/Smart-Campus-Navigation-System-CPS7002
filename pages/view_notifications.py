import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# ------------------ Config ------------------
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read / Write ------------------
def read_notifications():
    if os.path.exists(NOTIF_CSV_PATH):
        return pd.read_csv(NOTIF_CSV_PATH)
    return pd.DataFrame(columns=["id", "user_id", "message", "delivered"])


# ------------------ Table Generation ------------------
def generate_notifications_table(df):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("User ID", className="p-2 bg-light border"),
        html.Th("Message", className="p-2 bg-light border"),
        html.Th("Delivered", className="p-2 bg-light border"),
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
def layout():
    df = read_notifications()

    return dbc.Container([

        # Search Input
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
@callback(
    Output("table-notif", "children"),
    Input("search-notif", "value")
)
def search_notifications(text):
    df = read_notifications()
    if not text:
        return generate_notifications_table(df)

    t = text.lower()
    df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
    return generate_notifications_table(df)
