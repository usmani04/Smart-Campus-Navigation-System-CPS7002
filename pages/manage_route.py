import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

CSV_PATH = "data/routes.csv"
BLUE = "#2f80ed"
WHITE = "#ffffff"
LIGHT = "#f4f9ff"

def read_routes():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=["id", "start_location", "end_location", "distance_m", "accessible"])


def save_routes(df):
    df.to_csv(CSV_PATH, index=False)

def input_style():
    return {
        "flex": "1",
        "padding": "12px",
        "border": f"2px solid {BLUE}",
        "borderRadius": "8px"
    }


def header_style():
    return {
        "padding": "12px",
        "borderBottom": "2px solid #ccc",
        "background": LIGHT,
        "textAlign": "left"
    }


def cell_style():
    return {
        "padding": "12px",
        "borderBottom": "1px solid #eee"
    }


def edit_btn_style():
    return {
        "background": "#f2c94c",
        "color": "black",
        "border": "none",
        "padding": "4px 10px",
        "borderRadius": "6px",
        "cursor": "pointer",
        "marginRight": "6px"
    }


def delete_btn_style():
    return {
        "background": "#eb5757",
        "color": "white",
        "border": "none",
        "padding": "4px 10px",
        "borderRadius": "6px",
        "cursor": "pointer"
    }



def generate_table(df):
    header = html.Tr([
        html.Th("ID", style=header_style()),
        html.Th("Start", style=header_style()),
        html.Th("End", style=header_style()),
        html.Th("Distance (m)", style=header_style()),
        html.Th("Accessible", style=header_style()),
        html.Th("Actions", style=header_style()),
    ])

    rows = []
    for _, row in df.iterrows():
        rows.append(
            html.Tr([
                html.Td(row.id, style=cell_style()),
                html.Td(row.start_location, style=cell_style()),
                html.Td(row.end_location, style=cell_style()),
                html.Td(row.distance_m, style=cell_style()),
                html.Td(str(row.accessible), style=cell_style()),
                html.Td([
                    html.Button("Edit", id={"type": "edit", "index": int(row.id)}, style=edit_btn_style()),
                    html.Button("Delete", id={"type": "delete", "index": int(row.id)}, style=delete_btn_style())
                ])
            ])
        )

    return html.Table([header] + rows, style={"width": "100%", "borderCollapse": "collapse"})



def layout():
    df = read_routes()

    return html.Div(style={"padding": "20px"}, children=[

        html.Div(style={
            "background": WHITE,
            "padding": "25px",
            "borderRadius": "15px",
            "marginBottom": "25px"
        }, children=[
            html.H3("Add / Edit Route"),
            dcc.Store(id="edit-id", data=None),

            html.Div(style={"display": "flex", "gap": "15px", "marginBottom": "15px"}, children=[
                dcc.Input(id="start", placeholder="Start location", value="", style=input_style()),
                dcc.Input(id="end", placeholder="End location", value="", style=input_style()),
                dcc.Input(id="distance", type="number", placeholder="Distance (m)", value=None, style=input_style()),
                dcc.Dropdown(
                    id="accessible",
                    options=[
                        {"label": "Accessible", "value": True},
                        {"label": "Not Accessible", "value": False},
                    ],
                    value=None,
                    placeholder="Accessible",
                    style={"flex": "1"}
                )
            ]),

            html.Div(style={"textAlign": "right"}, children=[
                html.Button("Add", id="add-btn", n_clicks=0, style={
                    "background": BLUE,
                    "color": "white",
                    "border": "none",
                    "padding": "10px 25px",
                    "borderRadius": "8px"
                }),
                html.Button("Reset", id="reset-btn", n_clicks=0, style={
                    "background": "gray",
                    "color": "white",
                    "border": "none",
                    "padding": "10px 25px",
                    "borderRadius": "8px",
                    "marginLeft": "10px"
                })
            ]),

            html.Div(id="msg", style={"marginTop": "10px"})
        ]),

        dcc.Input(
            id="search",
            placeholder="Search routes...",
            value="",
            style={
                "width": "300px",
                "padding": "12px",
                "border": f"2px solid {BLUE}",
                "borderRadius": "8px",
                "marginBottom": "15px"
            }
        ),

        html.Div(id="table", children=generate_table(df))
    ])



@callback(
    Output("table", "children", allow_duplicate=True),
    Input({"type": "delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_route(clicks):
    if not any(clicks):
        raise PreventUpdate

    ctx = dash.callback_context
    route_id = ctx.triggered_id["index"]

    df = read_routes()
    df = df[df.id != route_id]
    save_routes(df)
    return generate_table(df)


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

    ctx = dash.callback_context
    route_id = ctx.triggered_id["index"]

    df = read_routes()
    r = df[df.id == route_id].iloc[0]

    return r.start_location, r.end_location, r.distance_m, r.accessible, "Update", route_id


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
        return dash.no_update, "Please fill all fields"

    df = read_routes()

    if edit_id is not None:
        df.loc[df.id == edit_id, ["start_location", "end_location", "distance_m", "accessible"]] = [s, e, d, a]
        msg = "Route updated"
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

    save_routes(df)
    return generate_table(df), msg


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


